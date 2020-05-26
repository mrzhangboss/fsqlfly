import json
import time
import logging
from copy import deepcopy
from collections import defaultdict
from datetime import datetime, date
from airflow.operators.sensors import BaseSensorOperator
from airflow.hooks.http_hook import HttpHook
from airflow.utils.decorators import apply_defaults


class _BaseJobOperator(BaseSensorOperator):
    template_fields = ['data', 'headers']
    RUN_STATUS = 'RUNNING'
    FINISHED_STATUS = 'FINISHED'

    @classmethod
    def gen_job_url(cls, job_name, method):
        return f'/api/transform/{method}/{job_name}'

    def get_connector_job_list(self, job_name):
        url = f'/api/connector/list/{job_name}'
        return self.http.run(url, headers=self.headers).json()['data']

    def get_all_job_names(self):
        raise NotImplementedError

    def get_job_list(self):
        if self.all_jobs is None:
            self.all_jobs = self.get_all_job_names()
        left_jobs = [x for x in self.all_jobs if x not in self.finished_jobs and x not in self.job_pools]
        return left_jobs

    def get_start_endpoint(self, job_name):
        return self.gen_job_url(job_name, 'start')

    def get_status_endpoint(self, job_name):
        return self.gen_job_url(job_name, 'status')

    def complete_job(self, job_name):
        self.finished_jobs.append(job_name)

    @apply_defaults
    def __init__(self, http_conn_id, token, job_name,
                 data=None, headers=None, method='start', daemon=True, parallelism=0, retry_times=3, retry_sleep_time=1,
                 *args, **kwargs):
        basic_headers = {'Content-Type': "application/json",
                         'Token': token}
        if headers:
            basic_headers.update(headers)
        self.headers = basic_headers
        self.http_conn_id = http_conn_id
        self.job_name = job_name
        self.http = HttpHook('POST', http_conn_id=self.http_conn_id)

        self.data = data if data is not None else {}
        self.job_last_run_id = dict()
        self.job_pools = []
        self.all_jobs = None
        self.finished_jobs = []
        self.parallelism = parallelism
        self.method = method
        self.daemon = daemon
        self.retry_times = retry_times
        self.retry_sleep_time = retry_sleep_time
        self.start_run_time = time.time()
        self.failed_jobs = defaultdict(int)

        super(_BaseJobOperator, self).__init__(*args, **kwargs)

    def get_req_data(self, job_name):
        def _parse_date_time(d):
            if isinstance(d, datetime) or isinstance(d, date):
                return str(d)

        send_data = deepcopy(self.data)
        last_run_job_id = self.job_last_run_id.get(job_name)
        if last_run_job_id:
            send_data['last_run_job_id'] = last_run_job_id
        if self.start_run_time:
            send_data['start_run_time'] = self.start_run_time

        return json.dumps(send_data, ensure_ascii=True, default=_parse_date_time)

    def run_other_mode(self):
        for job_name in self.get_job_list():
            res = self.http.run(self.gen_job_url(job_name, self.method)
                                , data=self.get_req_data(job_name), headers=self.headers).json()
            if not res['success']:
                raise Exception('{} Job Fail response: {}'.format(self.method, str(res)))
            else:
                print('Job {} {} Finished'.format(self.job_name, self.method))

    def execute(self, context):
        self.start_run_time = time.time()
        if self.method != 'start':
            return self.run_other_mode()
        super(_BaseJobOperator, self).execute(context)

    def get_job_status(self, job_name):
        res = self.http.run(self.get_status_endpoint(job_name), data=self.get_req_data(job_name),
                            headers=self.headers).json()
        full_msg = "req: {} code: {} msg: {}".format(job_name, res['code'], res['msg'])
        if not res['success']:
            raise Exception(full_msg)
        msg = res['msg']
        if msg.endswith(self.RUN_STATUS):
            job_id, _ = msg.split('_' + self.RUN_STATUS, 1)
            self.job_last_run_id[job_name] = job_id
        return msg

    def add_job_to_pool(self, job_name):
        status = self.get_job_status(job_name)
        if status.endswith(self.RUN_STATUS):
            raise Exception("Job {} Already {}".format(job_name, status))
        self.job_pools.append(job_name)

        res = self.http.run(self.get_start_endpoint(job_name), json=self.get_req_data(job_name),
                            headers=self.headers).json()
        if not res['success']:
            raise Exception('Start Job Fail response: {}'.format(str(res)))

    def pop_finished_job(self):
        current_size = len(self.job_pools)
        for _ in range(current_size):
            job_name = self.job_pools.pop(0)
            if self.daemon:
                msg = self.get_job_status(job_name)
                if msg == self.FINISHED_STATUS:
                    self.finished_jobs.append(job_name)
                elif msg.endswith(self.RUN_STATUS):
                    logging.debug("Wait For :" + msg)
                    self.job_pools.append(job_name)
                else:
                    if self.failed_jobs[job_name] < self.retry_times:
                        self.failed_jobs[job_name] += 1
                        time.sleep(self.retry_sleep_time)
                        self.job_pools.append(job_name)
                    else:
                        err_info = "Job {} Fail With Other Exception: {}".format(job_name, msg)
                        logging.error(err_info)
                        raise Exception(err_info)
            else:
                self.finished_jobs.append(job_name)

    def job_pool_finished(self):
        self.pop_finished_job()
        if self.get_job_list() or self.job_pools:
            return False
        return True

    def poke(self, context):
        run_jobs = self.get_job_list()
        while (len(self.job_pools) < self.parallelism or self.parallelism == 0) and run_jobs:
            job_name = run_jobs.pop()
            self.add_job_to_pool(job_name)
        return self.job_pool_finished()


class FSQLFlyOperator(_BaseJobOperator):
    def get_all_job_names(self):
        return [self.job_name]


class FSQLFlyConnectorOperator(_BaseJobOperator):
    def get_all_job_names(self):
        return self.get_connector_job_list(self.job_name)
