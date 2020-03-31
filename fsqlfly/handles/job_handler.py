# -*- coding:utf-8 -*-
import time
import traceback
from io import StringIO
from typing import List, Any
from requests import Session
from tornado.web import authenticated
from collections import namedtuple, defaultdict
from fsqlfly.settings import FSQLFLY_FINK_HOST
from fsqlfly.models import Transform
from fsqlfly.workflow import run_transform
from fsqlfly.base_handle import BaseHandler
from fsqlfly.utils.response import create_response

JobStatus = namedtuple('JobStatus', ['name', 'job_id', 'status'])

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
        self.host = FSQLFLY_FINK_HOST
        self.session = Session()
        self.cache = Cache()

    @property
    def job_status(self) -> List[JobStatus]:
        jobs_url = self.host + '/jobs'
        js = self.session.get(jobs_url).json()
        all_jobs = list()
        for x in js['jobs']:
            j_id = x['id']
            cache_name = '{}:flink:job:status'.format(j_id)
            if self.cache.get(cache_name) is None:
                status = self.session.get(self.host + '/jobs/' + j_id).json()
                name = status['name'].split(':', maxsplit=1)[0]
                self.cache.set(cache_name, name)
            else:
                name = self.cache.get(cache_name)
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


class JobHandler(BaseHandler):
    @authenticated
    def get(self, name: str, mode: str):
        handle_name = 'handle_' + mode
        if mode in JobControlHandle and handle_name in JobControlHandle:
            transform = Transform.select().where(Transform.name == name).first()
            if transform is None:
                return self.write_json(create_response(code=500, msg='job {} not found!!!'.format(name)))

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


class JobList(BaseHandler):
    @authenticated
    def get(self):
        jobs = defaultdict(lambda: defaultdict(int))
        job_names = {"{}_{}".format(x.id, x.name): x.name for x in
                     Transform.select().order_by(Transform.id.desc()).objects()}
        for job in JobControlHandle.job_status:

            if job.name in job_names or '_'.join(job.name.split('_')[:-1]) in job_names:
                print(job.name)
                jobs[job.status][job.name] += 1
        return self.write_json(dict(data=dict(jobs), code=0, success=0, msg=None))


default_handlers = [
    (r'/api/jobs/(?P<name>[\w_]+)/(?P<mode>\w+)', JobHandler),
    (r'/api/jobs', JobList),
]
