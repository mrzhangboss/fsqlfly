# -*- coding:utf-8 -*-
import json
import time
import threading
import pickle
import traceback
import attr
from io import StringIO
from typing import Tuple, Union, Optional, Type, Callable
from datetime import datetime
from functools import partial
from itertools import chain
from collections import defaultdict
from dbs.models import Connection, Relationship
from django.http import HttpRequest, JsonResponse
from django.db.models import Q
from utils.db_helper import DBProxy
from utils.response import create_response
from MySQLdb import ProgrammingError

global_proxy = threading.local()
PROXY_NAME = 'DB_PROXY_NAME'


class ProxyHelper:

    def __init__(self):
        self.last_connection_update_at = self.get_latest_field('update_at', Connection)
        self.last_relation_update_at = self.get_latest_field('update_at', Relationship)
        self.last_connection_create_at = self.get_latest_field('create_at', Connection)
        self.last_relation_create_at = self.get_latest_field('create_at', Relationship)
        self.cache = dict()
        self.relation = dict()

        for con in Connection.objects.filter(is_deleted=False, is_publish=True, is_available=True).all():
            if con.cache is None:
                continue
            key = self._get_connection_key(con)
            self.cache[key] = pickle.loads(con.cache)

        for relation in Relationship.objects.filter(is_deleted=False, is_publish=True, is_available=True).all():
            key = self._get_relation_key(relation)
            self.relation[key] = relation.get_cache()

        self._proxy = DBProxy(caches=list(self.cache.values()), assigned_relations=self.get_assigned_relations())

    def get_assigned_relations(self):
        return list(chain(*list(self.relation.values()))) if self.relation else None

    @classmethod
    def get_latest_field(cls,
                         field: str = 'create_at',
                         model: Union[Type[Connection], Type[Relationship]] = Connection) -> Optional[datetime]:
        data = model.objects.filter(is_deleted=False, is_publish=True, is_available=True).values(field).order_by(
            f'-{field}').first()
        if data:
            return data[field]
        return data

    @classmethod
    def _get_relation_key(cls, relation: Relationship) -> Tuple[str, int]:
        return relation.name, relation.create_by

    @classmethod
    def _get_connection_key(cls, con: Connection) -> Tuple[int, str]:
        return con.create_by, con.name

    def check_db_update(self) -> bool:
        update = self.check_connection_update()
        update = self.check_relation_update() or update

        return update

    def check_relation_update(self):
        update = False
        last_relation_update_at, last_relation_create_at = self.last_relation_update_at, self.last_relation_create_at
        self.last_relation_update_at = self.get_latest_field('update_at', Relationship)
        self.last_relation_create_at = self.get_latest_field('create_at', Relationship)
        for relation in Relationship.objects.filter(
                Q(update_at__gt=last_relation_update_at) | Q(create_at__gt=last_relation_create_at)).all():
            if relation.cache is None:
                continue
            update = True
            key = self._get_relation_key(relation)
            if relation.is_deleted != False or relation.is_publish != True or relation.is_available != True:
                key = self._get_connection_key(relation)
                if key in self.relation:
                    del self.relation[key]
            else:
                self.relation[key] = relation.get_cache()
        return update

    def check_connection_update(self):
        update = False
        last_connection_update_at, last_connection_create_at = self.last_connection_update_at, self.last_connection_create_at
        self.last_connection_update_at = self.get_latest_field('update_at', Connection)
        self.last_connection_create_at = self.get_latest_field('create_at', Connection)
        for con in Connection.objects.filter(
                Q(update_at__gt=last_connection_update_at) | Q(create_at__gt=last_connection_create_at)).all():
            if con.cache is None:
                continue
            update = True
            key = self._get_connection_key(con)
            if con.is_deleted != False or con.is_publish != True or con.is_available != True:
                key = self._get_connection_key(con)
                if key in self.cache:
                    del self.cache[key]
            else:
                self.cache[key] = pickle.loads(con.cache)
        return update

    def rebuild_proxy_cache(self):
        assigned_relations = self.get_assigned_relations()
        caches = list(self.cache.values())
        self._proxy.rebuild_cache(caches, assigned_relations)

    def generate_response(self, func: Callable) -> JsonResponse:
        try:
            data = func()
        except Exception as e:
            msg_io = StringIO()
            msg_io.write("Meet {}".format(str(e)))
            traceback.print_exc(file=msg_io)
            msg_io.seek(0)
            real_msg = msg_io.read()
            return create_response(data=None, code=500, msg=real_msg)
        else:
            return create_response(data=attr.asdict(data))

    def get_tables(self) -> JsonResponse:
        return self.generate_response(self._proxy.api_get_all_table_metas)

    def get_related_tables(self, table_name: str) -> JsonResponse:
        return self.generate_response(partial(self._proxy.api_get_related_table_metas, table_name))

    def search_table(self, source_table: str, search_text: str, target_table: str, limit: int) -> JsonResponse:
        return self.generate_response(
            partial(self._proxy.api_search_table, source_table=source_table, search=search_text,
                    target_table=target_table,
                    limit=limit))


def generate_proxy() -> ProxyHelper:
    return ProxyHelper()


def check_proxy_update(proxy: ProxyHelper) -> ProxyHelper:
    if proxy.check_db_update():
        proxy.rebuild_proxy_cache()
    return proxy


def get_proxy() -> ProxyHelper:
    if not hasattr(global_proxy, PROXY_NAME):
        setattr(global_proxy, PROXY_NAME, generate_proxy())
    proxy = getattr(global_proxy, PROXY_NAME)
    check_proxy_update(proxy)
    return proxy


def search(req: HttpRequest, table_name: str) -> JsonResponse:
    if req.body:
        data = json.loads(req.body)
    else:
        data = {}
    return get_proxy().search_table(source_table=data.get('selectTable', table_name),
                                    search_text=data.get('search', ''),
                                    target_table=table_name,
                                    limit=int(data.get('limit', '500')))


def list_tables(req: HttpRequest) -> JsonResponse:
    return get_proxy().get_tables()


def get_related_tables(req: HttpRequest, table_name: str) -> JsonResponse:
    return get_proxy().get_related_tables(table_name)
