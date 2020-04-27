# -*- coding:utf-8 -*-
from fsqlfly.common import safe_authenticated
from fsqlfly.base_handle import BaseHandler
from fsqlfly.common import DBRes


class ManagerHandler(BaseHandler):
    @safe_authenticated
    def post(self, model: str, mode: str, pk: str):
        print(model, mode, pk)
        return self.write_res(DBRes.sever_error())


default_handlers = [
    (r'/api/(?P<model>connection|name|template|version)/(?P<mode>update)/(?P<pk>\d+)', ManagerHandler),
]
