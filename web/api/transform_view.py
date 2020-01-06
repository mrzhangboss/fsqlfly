# -*- coding: utf-8 -*-
import os
import json
import random
import requests
from requests import Session
from datetime import datetime
from collections import namedtuple, defaultdict
from base64 import b64decode, b64encode
from typing import Optional, Union, List
from urllib.parse import quote
import yaml
from django.db.models import Model
from django.http import HttpRequest, JsonResponse
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


def get_list_or_create(req: HttpRequest) -> JsonResponse:
    if req.method == 'POST':
        data = json.loads(req.body)
        namespace = Namespace.objects.get(id=data['namespaceId']) if data['namespaceId'] else None
        obj = Transform.objects.create(name=data['name'], info=data['info'],
                                       sql=data['sql'], require=json.dumps(data['columns']),
                                       yaml=data['config'], namespace=namespace, is_publish=data['isPublish'],
                                       is_available=data['isAvailable'])
        return create_response(data={'id': obj.id, 'namespaceId': obj.namespace.id if obj.namespace else 0})
    res = []
    for sou in Transform.objects.filter(is_deleted=False).all():
        res.append({
            'id': sou.id,
            'name': sou.name,
            'namespaceId': sou.namespace.id if sou.namespace else 0,
            'info': sou.info,
            'isAvailable': sou.is_available,
            'isPublish': sou.is_publish,
            'createAt': str(sou.create_at),
            'updateAt': str(sou.update_at),
        })
    return create_response(data=res)


def debug_transform(req: HttpRequest) -> JsonResponse:
    data = json.loads(req.body)
    print(data)
    command, file_name = run_debug_transform(data)
    encode_file_name = quote(file_name)
    url = TERMINAL_WEB_HOST_FMT.format(b64encode(command.encode()).decode(), encode_file_name)
    return create_response(data={"url": url})


def start_run(req: HttpRequest, pk: int) -> JsonResponse:
    obj = Transform.objects.get(pk=pk)
    success, out = run_transform(obj)
    return create_response(msg=out, code=0 if success else 500)


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
        obj.require = json.dumps(data['columns'])
        namespace = Namespace.objects.get(id=data['namespaceId']) if data['namespaceId'] else None
        obj.namespace = namespace
        obj.sql = data['sql']
        assert check_yaml(data['config'])
        obj.yaml = data['config']
        obj.save()
    return create_response(data={'id': obj.id, 'namespaceId': obj.namespace.id if obj.namespace else 0})


JobStatus = namedtuple('JobStatus', ['name', 'job_id', 'status'])


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
        return '\n'.join(msgs)

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
        return '\n'.join(msgs)

    def handle_start(self, transform: Transform, **kwargs) -> str:
        return self.start_flink_job(transform, **kwargs)

    def stop_flink_jobs(self, job_ids: List):
        for j_id in job_ids:
            print('begin stop flink job', j_id)
            res = self.session.patch(self.host + '/jobs/' + j_id + '?mode=cancel')
            print(res.text)

    @classmethod
    def start_flink_job(cls, transform: Transform, **kwargs) -> str:
        is_ok, _ = run_transform(transform, **kwargs)
        return 'Job {} {}'.format(transform.name, 'success' if is_ok else 'fail')


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
        return create_response(msg=getattr(JobControlHandle, handle_name)(transform, **data))
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
