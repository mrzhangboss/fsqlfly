# -*- coding:utf-8 -*-
from fsqlfly.common import safe_authenticated
from fsqlfly.base_handle import BaseHandler
from fsqlfly.common import DBRes
from fsqlfly.connection_manager import ManagerFactory


class ManagerHandler(BaseHandler):
    @safe_authenticated
    def post(self, model: str, mode: str, pk: str):
        manager = ManagerFactory.get_manager(model, mode)
        if manager.is_support(pk):
            self.write_res(manager.run(pk))
        else:
            self.write_res(DBRes.api_error("{} {} not support now".format(model, mode)))


default_handlers = [
    (r'/api/(?P<model>\w+)/(?P<mode>update|clean|init|list)/(?P<pk>[a-zA-Z_0-9]+)', ManagerHandler),
]
