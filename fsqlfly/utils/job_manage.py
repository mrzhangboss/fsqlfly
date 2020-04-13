# -*- coding:utf-8 -*-
import time
import re
import math
import traceback
from io import StringIO
from typing import List, Any, Set
from collections import namedtuple, Counter
from datetime import datetime
from requests import Session
from logzero import logger
from fsqlfly.settings import FSQLFLY_FINK_HOST
from fsqlfly.models import Transform
from fsqlfly.workflow import run_transform
from fsqlfly.utils.strings import get_job_short_name
from fsqlfly.utils.response import create_response

JobStatus = namedtuple('JobStatus', ['name', 'job_id', 'status', 'full_name',
                                     'start_time', 'end_time', 'duration', 'pt'])
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
    status = 'status'
    RUN_STATUS = 'RUNNING'
    FINISHED_STATUS = 'FINISHED'
    DUPLICATE_RUN_STATUS = 'DUPLICATE_RUNNING'

    def __contains__(self, item):
        if hasattr(self, item):
            return True
        return False

    def __init__(self, flink_host=None):
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
        name = status['name'].split(':', maxsplit=1)[0]
        if '.' in name:
            name, pt = name.split('.', maxsplit=1)
        else:
            pt = None
        job_status = JobStatus(name, job_id, status['state'], full_name=status['name'],
                               start_time=p_time(status["start-time"]), end_time=p_time(status["end-time"]),
                               duration=p_duration(status['duration']), pt=pt)
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

    @property
    def live_job_names(self) -> Set[str]:
        data = set()
        for job in self.job_status:
            if job.status == 'RUNNING':
                data.add(job.name)
        return data

    def handle_restart(self, transform: Transform, **kwargs) -> str:
        msgs = []
        msgs.append(self.handle_stop(transform))
        msgs.append(self.start_flink_job(transform, **kwargs))
        return SUCCESS_HEADER + '\n'.join(msgs)

    def handle_stop(self, transform: Transform, **kwargs) -> str:
        msgs = []
        header = get_job_short_name(transform)
        kill_jobs = []
        job_status = self.job_status
        pt = kwargs['pt'] if 'pt' in kwargs else None
        kill_all_pt = True if 'kill_all_pt' in kwargs else False
        for job in job_status:
            if job.status == self.RUN_STATUS and job.name == header and (job.pt == pt or kill_all_pt):
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

    def handle_status(self, transform: Transform, **kwargs) -> str:
        header = get_job_short_name(transform)
        job_status = self.job_status
        pt = kwargs['pt'] if 'pt' in kwargs else None
        statuses = Counter()
        for job in job_status:
            if job.status == self.RUN_STATUS and job.name == header and job.pt == pt:
                statuses[job.status] += 1
        if statuses[self.RUN_STATUS] > 1:
            return self.DUPLICATE_RUN_STATUS
        if statuses[self.RUN_STATUS] == 1:
            return self.RUN_STATUS
        return self.FINISHED_STATUS

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

    job_pattern = re.compile(r'\d+_')

    @classmethod
    def is_real_job(cls, name) -> bool:
        return cls.job_pattern.search(name) is not None


JobControlHandle = JobControl(FSQLFLY_FINK_HOST)


def handle_job(mode: str, pk: str, json_body: dict) -> dict:
    handle_name = 'handle_' + mode
    if mode in JobControlHandle and handle_name in JobControlHandle:
        if pk.isdigit():
            transform = Transform.select().where(Transform.id == int(pk)).first()
            if transform is None:
                return create_response(code=500, msg='job id {} not found!!!'.format(pk))
        else:
            transform = pk

        data = json_body
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
