# -*- coding:utf-8 -*-
from fsqlfly.common import safe_authenticated
from fsqlfly.base_handle import BaseHandler
from fsqlfly.db_helper import SUPPORT_MODELS, DBDao


class APICounter(BaseHandler):
    @safe_authenticated
    def get(self):
        data = {k + 'Num': DBDao.count(v) for k, v in SUPPORT_MODELS.items()}
        data['code'] = 200
        data['success'] = True
        return self.write_json(data)


class CRHandler(BaseHandler):
    @safe_authenticated
    def get(self, model: str):
        self.write_res(DBDao.get(model))

    @safe_authenticated
    def post(self, model: str):
        self.write_res(DBDao.create(model, self.json_body))


class UDHandler(BaseHandler):
    @safe_authenticated
    def post(self, model: str, pk: int):
        self.write_res(DBDao.update(model, pk, self.json_body))

    @safe_authenticated
    def delete(self, model: str, pk: int):
        self.write_res(DBDao.delete(model, pk))


default_handlers = [
    (r'/api/count', APICounter),
    (r'/api/(?P<model>\w+)', CRHandler),
    (r'/api/(?P<model>\w+)/(?P<pk>\d+)', UDHandler),
]
