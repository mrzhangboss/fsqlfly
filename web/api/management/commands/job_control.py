# -*- coding: utf-8 -*-
import time
import os
import sys
import json
from typing import Optional
from collections import defaultdict
from requests import Session
from datetime import datetime
from random import randint
from django.core.management.base import BaseCommand, CommandError
from web.settings import ENV, TIME_FORMAT, FLINK_API_HOST
from dbs.workflow import run_transform
from dbs.models import Transform


class Command(BaseCommand):
    help = 'Job Damon'
    flink_api_host = "http://localhost:8081"

    def add_arguments(self, parser):
        parser.add_argument('--mode', action='store', help='mode',
                            choices=['damon'],
                            type=str,
                            default='damon')
        parser.add_argument('--debug', action='store_true', help='debug')

        parser.add_argument('--flink_api_host', action='store', help='flink api host',
                            default=None)

        parser.add_argument('--frequency', action='store', help='job damon sleep second',
                            default=30)

    def handle(self, *args, **options):
        host = options['flink_api_host']
        is_debug = options['debug']
        sleep = options['frequency']
        session = Session()
        if host is None:
            env_v = FLINK_API_HOST
            if env_v is None:
                host = self.flink_api_host
            else:
                host = env_v
        all_jobs = dict()
        while True:

            start_time = time.time()

            job_names = {"{}_{}".format(x.id, x.name): x for x in
                         Transform.objects.filter(is_publish=True, is_deleted=False, is_available=True).order_by(
                             '-id').all()}
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
                    print(datetime.now(), 'begin run ', k)
                    is_ok, r = run_transform(v)
                    if is_debug:
                        print(r)


            end_time = time.time()

            cost = end_time - start_time
            print(datetime.now().strftime(TIME_FORMAT), ' damon cost ', '%.2f' % cost, ' second')
            if cost < sleep:
                time.sleep(sleep - cost)
