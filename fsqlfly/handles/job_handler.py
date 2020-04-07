# -*- coding:utf-8 -*-
import time
import traceback
from io import StringIO
from typing import Dict
from tornado.web import authenticated
from collections import defaultdict
from fsqlfly.settings import FSQLFLY_FINK_HOST, TEMP_TERMINAL_HEAD
from fsqlfly.models import Transform, auto_close
from fsqlfly.base_handle import BaseHandler
from fsqlfly.utils.response import create_response
from fsqlfly.utils.job_manage import JobControlHandle, FAIL_HEADER


class JobHandler(BaseHandler):
    @authenticated
    @auto_close
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
    @authenticated
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

        return self.write_json(create_response(data=all_jobs))


default_handlers = [
    (r'/api/job/(?P<mode>\w+)/(?P<pk>[a-zA-Z0-9]+)', JobHandler),
    (r'/api/job', JobList),
]
