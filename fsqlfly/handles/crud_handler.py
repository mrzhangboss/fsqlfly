# -*- coding:utf-8 -*-
import json
import tornado.web
from terminado import TermSocket
from tornado.web import authenticated
from fsqlfly import settings
from fsqlfly.base_handle import BaseHandler, RespCode
from fsqlfly.models import Namespace, FileResource, Functions, Transform, Resource
from fsqlfly.utils.strings import dict2camel
from fsqlfly.utils.response import create_response

_MODELS = {
    'functions': Functions,
    'namespace': Namespace,
    'resource': Resource,
    'transform': Transform,
    'file': FileResource,
}


class APICounter(BaseHandler):
    @authenticated
    def get(self):
        data = {
            "namespaceNum": Namespace.select().where(Namespace.is_deleted==False).count(),
            "resourceNum": Resource.select().where(Resource.is_deleted==False).count(),
            "functionNum": Functions.select().where(Functions.is_deleted==False).count(),
            "fileNum": FileResource.select().where(FileResource.is_deleted==False).count(),
        }
        return self.write_json(create_response(data=data))


class CRHandler(BaseHandler):
    @authenticated
    def get(self, model: str):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        db = _MODELS[model]
        data = [dict2camel(x.to_dict()) for x in db.select().where(db.is_deleted == False).objects()]
        return self.write_json(create_response(data))

    @authenticated
    def post(self, model: str):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        print(self.json_body)
        _obj = _MODELS[model].create(
            **{k: v for k, v in self.json_body.items() if not (k.endswith('_id') and self.json_body[k] == 0)})
        self.write_json(create_response(data=_obj.to_dict()))


class UDHandler(BaseHandler):
    @authenticated
    def get(self, model: str, pk: int):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_json(dict(data=terms))

    @authenticated
    def post(self, model: str, pk: int):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_json(dict(data=terms))


default_handlers = [
    (r'/api/count', APICounter),
    (r'/api/(?P<model>\w+)', CRHandler),
    (r'/api/(?P<model>\w+)/(?P<pk>\d+)', UDHandler),
]
