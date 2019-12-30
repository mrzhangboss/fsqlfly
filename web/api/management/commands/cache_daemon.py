# -*- coding: utf-8 -*-
import time
import pickle
import traceback
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
from dbs.models import Transform, Connection, Relationship
from utils.db_crawler import Crawler


def safe_run(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print("Meet Exception", e)
        traceback.print_exc()
        return None


class Command(BaseCommand):
    help = 'Cache Damon'

    def add_arguments(self, parser):

        parser.add_argument('--debug', action='store_true', help='debug')

    def handle(self, *args, **options):
        debug = options['debug']
        run_history = defaultdict(int)

        crawler = Crawler()
        max_sleep, current_sleep = 10, 1

        while True:
            print('begin run ', datetime.now())

            updated = False

            def is_need_run(obj):
                res = obj.update_interval < 0 or time.time() > run_history[
                    (obj.create_by, obj.name)] + obj.update_interval
                run_history[(obj.create_by, obj.name)] = time.time()

                return res

            for con in Connection.objects.filter(is_deleted=False, is_publish=True, is_available=True).all():
                if is_need_run(con):
                    print('begin update ', con.typ, ' as ', con.name, con.suffix)
                    cache = safe_run(crawler.get_cache, con.url, con.suffix, con.typ, con.name, con.table_regex, con.table_exclude_regex)
                    if cache is not None:
                        con.cache = pickle.dumps(cache)
                        con.save()
                        updated = True

            if updated:
                current_sleep = 1
            else:
                current_sleep += 1
                current_sleep = min(max_sleep, current_sleep)
            time.sleep(current_sleep)

