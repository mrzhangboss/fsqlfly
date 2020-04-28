# -*- coding:utf-8 -*-
from fsqlfly.common import safe_authenticated
from fsqlfly.base_handle import BaseHandler
from fsqlfly.common import DBRes
from typing import Union
from fsqlfly.connection_manager import SUPPORT_MANAGER, NameFilter
from fsqlfly.db_helper import *


class ManagerHandler(BaseHandler):
    @safe_authenticated
    def post(self, model: str, mode: str, pk: str):
        if model not in SUPPORT_MODELS:
            return self.write_res(DBRes.api_error(msg='{} not support'.format(model)))
        session = DBSession.get_session()
        try:
            obj = DBDao.one(base=SUPPORT_MODELS[model], pk=int(pk), session=session)
            if isinstance(obj, Connection):
                name_filter = NameFilter(obj.include, obj.exclude)
                manager = SUPPORT_MANAGER[obj.type](obj.url, name_filter)
            elif isinstance(obj, ResourceName):
                name_filter = NameFilter(obj.get_include())
                manager = SUPPORT_MANAGER[obj.connection.type](obj.connection.url, name_filter)
            else:
                name_filter = NameFilter()
                typ = obj.connection.type
                manager = SUPPORT_MANAGER[typ](
                    obj.connection.url,
                    name_filter,
                    typ
                )

            self.write_res(manager.run(obj))
        finally:
            session.close()


default_handlers = [
    (r'/api/(?P<model>\w+)/(?P<mode>update)/(?P<pk>\d+)', ManagerHandler),
]
