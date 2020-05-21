# -*- coding:utf-8 -*-
from fsqlfly.common import safe_authenticated
from fsqlfly.base_handle import BaseHandler
from fsqlfly.common import PageModelMode, PageModel
from fsqlfly.version_manager.helpers.manager import ManagerHelper


class ManagerHandler(BaseHandler):
    @safe_authenticated
    def post(self, model: str, mode: str, pk: str):
        return self.write_res(ManagerHelper.run(model, mode, pk))


default_handlers = [
    (r'/api/(?P<model>{})/(?P<mode>{})/(?P<pk>[a-zA-Z_0-9]+)'.format(PageModel.regex(), PageModelMode.regex()),
     ManagerHandler),
]
