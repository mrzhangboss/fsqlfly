# -*- coding:utf-8 -*-
from fsqlfly.common import safe_authenticated
from fsqlfly.base_handle import BaseHandler
from fsqlfly.common import DBRes
from fsqlfly.connection_manager import ManagerHelper


class ManagerHandler(BaseHandler):
    @safe_authenticated
    def post(self, model: str, mode: str, pk: str):
        if ManagerHelper.is_support(mode):
            self.write_res(ManagerHelper.update(model, pk))
        else:
            self.write_res(DBRes.api_error("{} not support now".format(mode)))


default_handlers = [
    (r'/api/(?P<model>\w+)/(?P<mode>update)/(?P<pk>\d+)', ManagerHandler),
]
