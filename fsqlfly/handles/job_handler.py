# -*- coding:utf-8 -*-
import time
from io import StringIO
from typing import Dict, Optional, Any
from fsqlfly.common import safe_authenticated
from collections import defaultdict
from fsqlfly.settings import FSQLFLY_FINK_HOST, TEMP_TERMINAL_HEAD
from fsqlfly.base_handle import BaseHandler
from fsqlfly.utils.job_manage import JobControlHandle, handle_job
from fsqlfly.db_helper import DBDao
from fsqlfly.common import DBRes


class JobHandler(BaseHandler):
    @safe_authenticated
    def get(self, mode: str, pk: str):
        return self.write_res(handle_job(mode, pk, self.json_body))

    post = get


def get_latest_transform(refresh_seconds: int = 5) -> Dict[str, dict]:
    def _get():
        job_infos = defaultdict(dict)
        for x in DBDao.get_transform():
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
    @safe_authenticated
    def get(self):
        job_infos = get_latest_transform()
        all_jobs = list()
        for job in JobControlHandle.job_status:
            if not JobControlHandle.is_real_job(job.name):
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

        return self.write_res(DBRes(data=all_jobs))


default_handlers = [
    (r'/api/job/(?P<mode>\w+)/(?P<pk>[a-zA-Z0-9]+)', JobHandler),
    (r'/api/job', JobList),
]
