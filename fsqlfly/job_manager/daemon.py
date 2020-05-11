import time
import logging
import logzero
from tornado import ioloop
from logzero import setup_logger
from collections import defaultdict
from typing import Callable, Optional
# from fsqlfly.models import Transform, auto_close
from requests import Session
from datetime import datetime, date
from fsqlfly.workflow import run_transform
from fsqlfly.settings import FSQLFLY_DEBUG, FSQLFLY_MAIL_ENABLE
from fsqlfly.utils.job_manage import JobControlHandle
from fsqlfly.contrib.mail import MailHelper
from fsqlfly.db_helper import DBSession, DBDao


def get_log_file(file: str):
    return setup_logger(name='JobDaemon', logfile=file, maxBytes=int(1e6), backupCount=3,
                        level=logging.DEBUG if FSQLFLY_DEBUG else logging.INFO)


class FlinkJobDaemon:

    def __init__(self,
                 flink_host: str,
                 max_try: int,
                 login_file: str,
                 max_req_try: int = 5,
                 stop_handle: Optional[Callable] = None):
        self.logger = get_log_file(login_file)
        self.flink_host = flink_host
        self.max_try = max_try
        self.stop_handle = stop_handle
        self.max_req_try = max_req_try
        self.session = Session()
        self.run_times = defaultdict(lambda: defaultdict(int))
        self.started_jobs = set()

    def request(self, func: Callable, try_times: int = 0):
        try:
            return func()
        except Exception as err:
            if try_times > self.max_req_try:
                print('Meet Exception please check FSQLFLY_FINK_HOST is correct')
                raise err
            else:
                return self.request(func, try_times + 1)

    @classmethod
    def send_email(cls, title: str = '', content: str = ''):
        if FSQLFLY_MAIL_ENABLE:
            print(MailHelper.send(title, content))

    def run(self):
        self.logger.debug('Start Running Flink Job Damon {}'.format(str(datetime.now())[:19]))

        today = str(date.today())
        start_time = time.time()
        session = DBSession.get_session()
        job_names = DBDao.get_job_names(session=session)

        living_job = JobControlHandle.live_job_names
        for k, transform in job_names.items():
            if k not in living_job:
                if self.run_times[today][k] > self.max_try:
                    self.logger.error('job run too many times one day {}'.format(k))
                    self.send_email('job run too many times one day {}'.format(k))
                else:
                    self.run_times[today][k] += 1
                    self.logger.info('job {} begin run '.format(k))
                    is_ok, r = run_transform(transform)
                    if not is_ok:
                        self.send_email('job start fail {}'.format(k), r)
                        self.logger.error(r)
                    else:
                        if k in self.started_jobs:
                            self.send_email('try restart job {}, last fail'.format(k), r)
                        else:
                            self.started_jobs.add(k)
                    if self.stop_handle:
                        self.stop_handle(k)

        end_time = time.time()

        cost = end_time - start_time

        self.logger.debug(
            " ".join([str(datetime.now())[:19], ' damon cost ', '%.2f' % cost, ' second', ' will sleep ']))
        session.close()

    def get_periodic_callback(self, period) -> Callable:
        def _warp():
            ioloop.PeriodicCallback(self.run, period * 1000).start()

        return _warp
