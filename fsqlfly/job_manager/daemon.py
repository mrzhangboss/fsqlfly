import time
import logzero
from logzero import logger
from functools import partial
from collections import defaultdict
from typing import Callable, Optional
from fsqlfly.models import Transform
from requests import Session
from datetime import datetime, date
from fsqlfly.workflow import run_transform


def _set_log_file(file: str):
    logzero.logfile(file, maxBytes=int(1e6), backupCount=3)


class FlinkJobDaemon:

    def __init__(self,
                 flink_host: str,
                 frequency: int,
                 max_try: int,
                 login_file: str,
                 max_req_try: int = 5,
                 stop_handle: Optional[Callable] = None):
        _set_log_file(login_file)
        self.flink_host = flink_host
        self.frequency = frequency
        self.max_try = max_try
        self.stop_handle = stop_handle
        self.max_req_try = max_req_try
        self.session = Session()

    def request(self, func: Callable, try_times: int = 0):
        try:
            return func()
        except Exception as err:
            if try_times > self.max_req_try:
                print('Meet Exception please check FSQLFLY_FINK_HOST is correct')
                raise err
            else:
                return self.request(func, try_times + 1)

    def run(self):
        host = self.flink_host
        sleep = self.frequency
        max_print_times, print_times = max(60 / sleep, 1), 0
        session = Session()
        logger.info('Start Running Flink Job Damon')
        all_jobs = dict()
        run_times = defaultdict(lambda: defaultdict(int))
        while True:
            today = str(date.today())
            start_time = time.time()
            query = (Transform.is_publish == True, Transform.is_deleted == False, Transform.is_available == True)
            job_names = {"{}_{}".format(x.id, x.name): x for x in
                         Transform.select().where(*query).order_by(Transform.id.desc()).objects()}

            jobs_url = host + '/jobs'
            js = session.get(jobs_url).json()
            for x in js['jobs']:
                j_id = x['id']
                if j_id not in all_jobs:
                    all_jobs[j_id] = session.get(host + '/jobs/' + j_id).json()
                else:
                    all_jobs[j_id]['state'] = x['status']

            run_jobs = set()
            for k, v in all_jobs.items():
                full_name = v['name']
                for name, obj in job_names.items():
                    if full_name.startswith(name):
                        if v['state'] == 'RUNNING':
                            run_jobs.add(name)

            for k, v in job_names.items():
                if k not in run_jobs:
                    if run_times[today][k] > self.max_try:
                        logger.error('job run too many times one day {}'.format(k))
                    else:
                        run_times[today][k] += 1
                        logger.info('job {} begin run '.format(k))
                        is_ok, r = run_transform(v)
                        if not is_ok:
                            logger.error(r)
                        if self.stop_handle:
                            self.stop_handle(k)

            end_time = time.time()

            cost = end_time - start_time

            if print_times > max_print_times:
                logger.info(" ".join([str(datetime.now())[:19], ' damon cost ', '%.2f' % cost, ' second', ' will sleep ', str(int(sleep - cost))]))
                print_times = 0
            else:
                print_times += 1

            if cost < sleep:
                time.sleep(sleep - cost)
