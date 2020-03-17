# -*- coding: utf-8 -*-
import os
import json
import random
import requests
import traceback
from io import StringIO
from requests import Session
from datetime import datetime
from collections import namedtuple, defaultdict
from base64 import b64decode, b64encode
from typing import Optional, Union, List
from urllib.parse import quote
import yaml
from django.db.models import Model
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.core.cache import caches, cache
from dbs.models import Namespace, FileResource, Functions, Transform, Resource
from utils.response import create_response
from utils.strings import check_yaml, dict2underline, get_schema, get_sink_config
from dbs.workflow import run_transform, run_debug_transform
from web.settings import TERMINAL_WEB_HOST_FMT
from dbs.workflow import handle_template


def get_row_proc_columns_from_yaml(s: str) -> tuple:
    # todo: parse rowtime and proctime
    rowtime, proctime, columns = '', '', []
    schema = get_schema(s)
    for sc in schema:
        if sc['type'] in ['DATE', 'TIMESTAMP', 'TIME']:
            columns.append(sc)
        if 'rowtime' in sc:
            rowtime = sc['name']
        if 'proctime' in sc:
            proctime = sc['name']

    return rowtime, proctime, columns


def random_name(prefix='auto_generate'):
    rid = random.randint(100000, 999999)
    first = Transform.objects.order_by('-id').first()
    fid = first.id + 1 if first else 0
    return f'{prefix}_{fid}_{rid}'


def init_sink(transform_name: str, model: Optional[Resource], sink_yaml, namespace: Optional[Model] = None) -> Model:
    config = get_sink_config(sink_yaml)
    name = config['name'] if 'name' in config else transform_name
    if 'format' not in config:
        config['format'] = {'property-version': 1, 'type': 'json', 'derive-schema': True}

    new_yaml = yaml.dump(config)
    if model is None:
        model = Resource.objects.create(name=name, info='auto generate {}'.format(datetime.now()),
                                        yaml=new_yaml, namespace=namespace, typ='sink-table')
    else:
        model.name = name
        model.yaml = new_yaml
        model.namespace = namespace
        model.save()
    return model


def get_info(req: HttpRequest) -> JsonResponse:
    namespaces = [{'name': x.name, 'id': x.id} for x in Namespace.objects.filter(is_deleted=False).all()]
    sources = []
    ids = Resource.objects.filter(is_deleted=False).values('id')
    for x in ids:
        sou = Resource.objects.get(pk=x['id'])
        data = {
            'id': sou.id,
            'name': sou.name,
            'namespaceId': sou.namespace.id if sou.namespace else 0,
            'namespace': sou.namespace.name if sou.namespace else 'DEFAULT',
            'info': sou.info,
            'disabled': not sou.is_available,
            'avatar': sou.namespace.avatar if sou.namespace else '',
        }
        sources.append(data)

    return create_response(data={'namespaces': namespaces, 'columns': sources})


def test_require(require: str) -> Union[str, bool]:
    errors = []
    if require:
        for x in require.split(','):
            if '.' in x:
                space, name = x.split('.', 1)
            else:
                space, name = None, x

            if space:
                space = Namespace.objects.filter(name=space).first()
                if space is None:
                    errors.append('In {} error: namespace {} not exists'.format(x, space))

            resource = Resource.objects.filter(name=name, namespace=space).first()
            resource_only_name = Resource.objects.filter(name=name).first()
            if resource is None and resource_only_name is None:
                errors.append('In {} error: resource {} not exists'.format(x, name))

    if errors:
        return '\n'.join(errors)

    return True


def get_list_or_create(req: HttpRequest) -> JsonResponse:
    if req.method == 'POST':

        data = json.loads(req.body)
        require = data['require']

        test_result = test_require(require)
        if isinstance(test_result, str):
            return create_response(code=500, msg=test_result)

        namespace = Namespace.objects.get(id=data['namespaceId']) if data['namespaceId'] else None
        obj = Transform.objects.create(name=data['name'], info=data['info'],
                                       sql=data.get('sql', ''), require=require,
                                       yaml=data.get('yaml', ''), namespace=namespace, is_publish=data['isPublish'],
                                       is_available=data['isAvailable'])
        return create_response(data={'id': obj.id, 'namespaceId': obj.namespace.id if obj.namespace else 0})
    res = []
    for sou in Transform.objects.filter(is_deleted=False).all():
        res.append({
            'id': sou.id,
            'name': sou.name,
            'require': sou.require,
            'sql': sou.sql,
            'yaml': sou.yaml,
            'namespaceId': sou.namespace.id if sou.namespace else 0,
            'info': sou.info,
            'isAvailable': sou.is_available,
            'isPublish': sou.is_publish,
            'createAt': str(sou.create_at),
            'updateAt': str(sou.update_at),
        })
    return create_response(data=res)


def debug_transform(req: HttpRequest, pk: int) -> JsonResponse:
    data = json.loads(req.body)
    print(data)
    try:
        command, file_name = run_debug_transform(data)
    except Exception as err:
        out = StringIO()
        traceback.print_exc(file=out)
        out.seek(0)
        msg = out.read()
        return create_response(code=500, msg=msg)
    encode_file_name = quote(file_name)
    url = TERMINAL_WEB_HOST_FMT.format(b64encode(command.encode()).decode(), encode_file_name)
    return create_response(data={"url": url})


def get_job_redirect(pk: int, method: str):
    obj = Transform.objects.get(pk=pk)
    return HttpResponseRedirect('/api/jobs/{}/{}'.format(obj.name, method))


def start_run(req: HttpRequest, pk: int) -> HttpResponseRedirect:
    return get_job_redirect(pk, 'start')


def stop_run(req: HttpRequest, pk: int) -> HttpResponseRedirect:
    return get_job_redirect(pk, 'stop')


def restart_run(req: HttpRequest, pk: int) -> HttpResponseRedirect:
    return get_job_redirect(pk, 'restart')


def get_or_update_or_delete(req: HttpRequest, pk: int) -> JsonResponse:
    obj = Transform.objects.get(pk=pk)
    if req.method == 'GET':
        return create_response(data={
            'detail': {
                'sql': obj.sql,
                'config': '' if obj.yaml is None else obj.yaml
            },
            'resources': {
                'columns': json.loads(obj.require)
            }
        })
    elif req.method == 'DELETE':
        obj.is_deleted = True
        obj.save()
    else:
        data = json.loads(req.body)
        obj.name = data['name']
        obj.info = data['info']
        obj.is_available = data['isAvailable']
        obj.is_publish = data['isPublish']
        require = data['require']
        test_result = test_require(require)
        if isinstance(test_result, str):
            return create_response(code=500, msg=test_result)
        obj.require = require
        namespace = Namespace.objects.get(id=data['namespaceId']) if data['namespaceId'] else None
        obj.namespace = namespace
        obj.sql = data['sql']
        assert check_yaml(data['yaml'])
        obj.yaml = data['yaml']
        obj.save()
    return create_response(data={'id': obj.id, 'namespaceId': obj.namespace.id if obj.namespace else 0})


JobStatus = namedtuple('JobStatus', ['name', 'job_id', 'status'])

FAIL_HEADER = 'FAIL:'
SUCCESS_HEADER = 'SUCCESS:'


class JobControl:
    restart = 'restart'
    stop = 'stop'
    start = 'start'
    RUN_STATUS = 'RUNNING'

    def __contains__(self, item):
        if hasattr(self, item):
            return True
        return False

    def __init__(self, flink_host=None):
        from web.settings import FLINK_API_HOST
        if flink_host is None:
            flink_host = FLINK_API_HOST
        assert flink_host is not None
        self.host = flink_host
        self.session = Session()

    @property
    def job_status(self) -> List[JobStatus]:
        jobs_url = self.host + '/jobs'
        js = self.session.get(jobs_url).json()
        all_jobs = list()
        for x in js['jobs']:
            j_id = x['id']
            cache_name = '{}:flink:job:status'.format(j_id)
            if cache.get(cache_name) is None:
                status = self.session.get(self.host + '/jobs/' + j_id).json()
                name = status['name'].split(':', maxsplit=1)[0]
                cache.set(cache_name, name)
            else:
                name = cache.get(cache_name)
            all_jobs.append(JobStatus(name, j_id, x['status']))
        return all_jobs

    @classmethod
    def get_job_header(cls, transform: Transform, **kwargs) -> str:
        return "{}_{}{}".format(transform.id, transform.name, '_' + kwargs['pt'] if 'pt' in kwargs else '')

    def handle_restart(self, transform: Transform, **kwargs) -> str:
        msgs = []
        msgs.append(self.handle_stop(transform))
        msgs.append(self.start_flink_job(transform, **kwargs))
        return SUCCESS_HEADER + '\n'.join(msgs)

    def handle_stop(self, transform: Transform, **kwargs) -> str:
        msgs = []
        header = self.get_job_header(transform, **kwargs)
        kill_jobs = []
        job_status = self.job_status
        for job in job_status:
            if job.name == header and job.status == self.RUN_STATUS:
                print('add a {} to kill '.format(job.name))
                kill_jobs.append(job.job_id)

        msgs.append('kill {} jobs: {}'.format(len(kill_jobs), ', '.join(str(x) for x in kill_jobs)))

        self.stop_flink_jobs(kill_jobs)
        return SUCCESS_HEADER + '\n'.join(msgs)

    def handle_start(self, transform: Transform, **kwargs) -> str:
        return self.start_flink_job(transform, **kwargs)

    def stop_flink_jobs(self, job_ids: List):
        for j_id in job_ids:
            print('begin stop flink job', j_id)
            res = self.session.patch(self.host + '/jobs/' + j_id + '?mode=cancel')
            print(res.text)

    @classmethod
    def start_flink_job(cls, transform: Transform, **kwargs) -> str:
        is_ok, txt = run_transform(transform, **kwargs)
        return '{} JOB {}\n{}'.format(SUCCESS_HEADER if is_ok else FAIL_HEADER, transform.name, '' if is_ok else txt)


JobControlHandle = JobControl()


def job_control_api(req: HttpRequest, name: str, mode: str) -> JsonResponse:
    handle_name = 'handle_' + mode
    if mode in JobControlHandle and handle_name in JobControlHandle:
        transform = Transform.objects.filter(name=name).first()
        if transform is None:
            return create_response(code=500, msg='job {} not found!!!'.format(name))
        if req.body:
            data = json.loads(req.body)
        else:
            data = dict()
        try:
            run_res = getattr(JobControlHandle, handle_name)(transform, **data)
        except Exception as e:
            out = StringIO()
            traceback.print_exc(file=out)
            out.seek(0)
            return create_response(msg=out.read(), code=500)
        return create_response(msg=run_res, code=500 if run_res.startswith(FAIL_HEADER) else 0)
    else:
        return create_response(code=500, msg=' {} not support!!!'.format(mode))


def job_list(req: HttpRequest) -> JsonResponse:
    jobs = defaultdict(lambda: defaultdict(int))
    job_names = {"{}_{}".format(x.id, x.name): x.name for x in
                 Transform.objects.all().order_by(
                     '-id').all()}
    for job in JobControlHandle.job_status:

        if job.name in job_names or '_'.join(job.name.split('_')[:-1]) in job_names:
            print(job.name)
            jobs[job.status][job.name] += 1
    return JsonResponse(dict(data=dict(jobs), code=0, success=0, msg=None))
