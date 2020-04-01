# -*- coding:utf-8 -*-
import time
import re
import traceback
import math
from io import StringIO
from typing import List, Any, Dict
from datetime import datetime
from requests import Session
from logzero import logger
from tornado.web import authenticated
from collections import namedtuple, defaultdict
from fsqlfly.settings import FSQLFLY_FINK_HOST, TEMP_TERMINAL_HEAD
from fsqlfly.models import Transform
from fsqlfly.workflow import run_transform
from fsqlfly.base_handle import BaseHandler
from fsqlfly.utils.response import create_response

JobStatus = namedtuple('JobStatus', ['name', 'job_id', 'status', 'full_name',
                                     'start_time', 'end_time', 'duration'])

FAIL_HEADER = 'FAIL:'
SUCCESS_HEADER = 'SUCCESS:'


class Cache:
    def __init__(self, max_store_seconds=5):
        self.time = dict()
        self.store = dict()
        self._max = max_store_seconds

    def get(self, name: str) -> Any:
        if name not in self.store:
            return None
        assert name in self.time
        if (time.time() - self.time[name]) > self._max:
            del self.time[name]
            del self.store[name]
            return None
        return self.store[name]

    def set(self, name: str, value: Any):
        self.store[name] = value
        self.time[name] = time.time()

    def remove(self, name: str):
        if name in self.time:
            del self.time[name]
        if name in self.store[name]:
            del self.store[name]


class JobControl:
    restart = 'restart'
    stop = 'stop'
    start = 'start'
    cancel = 'cancel'
    RUN_STATUS = 'RUNNING'

    def __contains__(self, item):
        if hasattr(self, item):
            return True
        return False

    def __init__(self, flink_host=None):
        print(flink_host)
        self.host = flink_host
        self.session = Session()
        self.cache = Cache()

    def _get_job_status(self, job_id: str) -> JobStatus:
        def p_time(t: int) -> str:
            return str(datetime.fromtimestamp(t / 1000))[:19] if t > 0 else '-'

        def p_duration(t: int) -> str:
            second = 1000
            minute = second * 60
            hour = minute * 60
            day = hour * 24
            out = list()
            for a, b in [(day, '天'), (hour, '小时'), (minute, '分')]:
                cost = 0
                while t > a:
                    cost += 1
                    t -= a
                if cost > 0:
                    out.append(f'{cost}{b}')
            out.append('{}秒'.format(math.ceil(t / second)))
            return ''.join(out)

        status = self.session.get(self.host + '/jobs/' + job_id).json()
        name = status['name'].split('.', maxsplit=1)[0]
        job_status = JobStatus(name, job_id, status['state'], full_name=status['name'],
                               start_time=p_time(status["start-time"]), end_time=p_time(status["end-time"]),
                               duration=p_duration(status['duration']))
        return job_status

    @property
    def job_status(self) -> List[JobStatus]:
        jobs_url = self.host + '/jobs'
        js = self.session.get(jobs_url).json()
        all_jobs = list()
        for x in js['jobs']:
            j_id = x['id']
            if self.cache.get(j_id) is None:
                status = self._get_job_status(j_id)
                self.cache.set(j_id, status)
            else:
                status = self.cache.get(j_id)

            all_jobs.append(status)
        return all_jobs

    @classmethod
    def get_job_header(cls, transform: Transform, **kwargs) -> str:
        return "{}_{}.{}-".format(transform.id, transform.name, '_' + kwargs['pt'] if 'pt' in kwargs else '')

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
            if job.status == self.RUN_STATUS and job.name == header:
                logger.debug('add a {} to kill '.format(job.name))
                kill_jobs.append(job.job_id)

        msgs.append('kill {} jobs: {}'.format(len(kill_jobs), ', '.join(str(x) for x in kill_jobs)))

        self.stop_flink_jobs(kill_jobs)
        return SUCCESS_HEADER + '\n'.join(msgs)

    def handle_start(self, transform: Transform, **kwargs) -> str:
        return self.start_flink_job(transform, **kwargs)

    def handle_cancel(self, jid: str, **kwargs):
        self.stop_flink_jobs([jid])
        return 'kill {} '.format(jid)

    def stop_flink_jobs(self, job_ids: List):
        for j_id in job_ids:
            logger.debug('begin stop flink job {}'.format(j_id))
            logger.debug(self.host)
            res = self.session.patch(self.host + '/jobs/' + j_id + '?mode=cancel')
            self.cache.remove(j_id)
            print(res.text)

    @classmethod
    def start_flink_job(cls, transform: Transform, **kwargs) -> str:
        is_ok, txt = run_transform(transform, **kwargs)
        return '{} JOB {}\n{}'.format(SUCCESS_HEADER if is_ok else FAIL_HEADER, transform.name, '' if is_ok else txt)


JobControlHandle = JobControl(FSQLFLY_FINK_HOST)


class JobHandler(BaseHandler):
    @authenticated
    def get(self, mode: str, pk: str):
        handle_name = 'handle_' + mode
        if mode in JobControlHandle and handle_name in JobControlHandle:
            if pk.isdigit():
                transform = Transform.select().where(Transform.id == int(pk)).first()
                if transform is None:
                    return self.write_json(create_response(code=500, msg='job id {} not found!!!'.format(pk)))
            else:
                transform = pk

            data = self.json_body
            try:
                run_res = getattr(JobControlHandle, handle_name)(transform, **data)
            except Exception as e:
                out = StringIO()
                traceback.print_exc(file=out)
                out.seek(0)
                return create_response(msg=out.read(), code=500)
            return self.write_json(create_response(msg=run_res, code=500 if run_res.startswith(FAIL_HEADER) else 0))
        else:
            return self.write_json(create_response(code=500, msg=' {} not support!!!'.format(mode)))

    post = get


def get_latest_transform(refresh_seconds: int = 5) -> Dict[str, dict]:
    def _get():
        job_infos = defaultdict(dict)
        for x in Transform.select().order_by(Transform.id.desc()).objects():
            name = "{}_{}".format(x.id, x.name)
            job_infos[name] = x.to_dict()
        return job_infos

    __name = '__transforms'
    if not hasattr(get_latest_transform, __name):
        setattr(get_latest_transform, __name, (_get(), time.time()))
    objects, t = getattr(get_latest_transform, __name)
    if time.time() - t > refresh_seconds:
        objects = _get()
        setattr(get_latest_transform, __name, (objects, time.time()))
    return objects


class JobList(BaseHandler):
    job_pattern = re.compile(r'\d+_')
    @classmethod
    def is_real_job(cls, name) -> bool:
        return cls.job_pattern.search(name) is not None

    @authenticated
    def get(self):
        target = self.request.arguments.get('id')
        id_filter = target[0].decode() if target else None

        job_infos = get_latest_transform()
        all_jobs = list()
        for job in JobControlHandle.job_status:
            if not self.is_real_job(job.name):
                continue
            if id_filter is not None and not job.name.startswith(id_filter + '_'):
                continue
            base = dict(**job._asdict())
            if job.name in job_infos:
                base.update(job_infos[job.name])
                base['t_id'] = job_infos[job.name]['id']
            elif job.name.startswith(TEMP_TERMINAL_HEAD):
                base['name'] = 'TEMPORARY'
                base['url'] = '/terminal/{}'.format(job.name[len(TEMP_TERMINAL_HEAD):])

            base['id'] = job.job_id
            base['detail_url'] = FSQLFLY_FINK_HOST + '/#/job/{}/overview'.format(job.job_id)

            all_jobs.append(base)

        return self.write_json(create_response(data=all_jobs))


default_handlers = [
    (r'/api/job/(?P<mode>\w+)/(?P<pk>[a-zA-Z0-9]+)', JobHandler),
    (r'/api/job', JobList),
]
