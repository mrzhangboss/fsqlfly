import json
import logging
from datetime import datetime, date
from airflow.operators.sensors import BaseSensorOperator
from airflow.hooks.http_hook import HttpHook
from airflow.utils.decorators import apply_defaults


class FSQLFlayOperator(BaseSensorOperator):
    template_fields = ['data', 'headers']
    RUN_STATUS = 'RUNNING'

    @classmethod
    def gen_job_url(cls, job_name, method):
        return f'/api/transform/{method}/{job_name}'

    @apply_defaults
    def __init__(self, http_conn_id, token, job_name, data=None, headers=None, *args, **kwargs):
        basic_headers = {'Content-Type': "application/json",
                         'Token': token}
        if headers:
            basic_headers.update(headers)
        self.headers = basic_headers
        self.start_endpoint = self.gen_job_url(job_name, 'start')
        self.status_endpoint = self.gen_job_url(job_name, 'status')
        self.http_conn_id = http_conn_id
        self.job_name = job_name
        self.http = HttpHook('POST', http_conn_id=self.http_conn_id)

        self.data = data if data is not None else {}

        super(FSQLFlayOperator, self).__init__(*args, **kwargs)

    @property
    def req_data(self):
        def _parse_date_time(d):
            if isinstance(d, datetime) or isinstance(d, date):
                return str(d)

        return json.dumps(self.data, ensure_ascii=True, default=_parse_date_time)

    def execute(self, context):
        print('data is ' + self.req_data, ' data type ', isinstance(self.req_data, str), type(self.req_data))
        status = self.get_job_status()
        if status.endswith(self.RUN_STATUS):
            raise Exception("Job {} Already {}".format(self.job_name, status))
        res = self.http.run(self.start_endpoint, data=self.req_data, headers=self.headers).json()
        if not res['success']:
            raise Exception('Start Job Fail response: {}'.format(str(res)))
        super(FSQLFlayOperator, self).execute(context)

    def get_job_status(self):
        res = self.http.run(self.status_endpoint, data=self.req_data, headers=self.headers).json()
        full_msg = "req: {} code: {} msg: {}".format(self.status_endpoint, res['code'], res['msg'])
        if not res['success']:
            raise Exception(full_msg)
        return res['msg']

    def poke(self, context):
        msg = self.get_job_status()
        if msg.endswith('RUNNING'):
            if msg != 'RUNNING':
                raise Exception(msg)
            return False
        logging.debug("Wait For :" + msg)
        return True
