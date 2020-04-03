# -*- coding:utf-8 -*-
import json
import tornado.web
from terminado import TermSocket
from tornado.web import authenticated
from logzero import logger
from fsqlfly import settings
from fsqlfly.base_handle import BaseHandler, RespCode
from fsqlfly.models import Namespace, FileResource, Functions, Transform, Resource
from fsqlfly.utils.strings import dict2camel, dict2underline
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
            "namespaceNum": Namespace.select().where(Namespace.is_deleted == False).count(),
            "resourceNum": Resource.select().where(Resource.is_deleted == False).count(),
            "functionNum": Functions.select().where(Functions.is_deleted == False).count(),
            "fileNum": FileResource.select().where(FileResource.is_deleted == False).count(),
            "transformNum": Transform.select().where(Transform.is_deleted == False).count(),
            "code": 200, "success": True
        }
        return self.write_json(data)


class CRHandler(BaseHandler):
    @authenticated
    def get(self, model: str):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)

        db = _MODELS[model]
        data = [x.to_dict(to_camel=True) for x in db.select().where(db.is_deleted == False).objects()]
        return self.write_json(create_response(data))

    @authenticated
    def post(self, model: str):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        data = dict2underline(self.json_body)
        same_obj = _MODELS[model].select().where(_MODELS[model].name == data['name']).first()
        if same_obj:
            logger.debug('try create a same name obj {} @{}'.format(same_obj.name, model))
            if same_obj.is_deleted:
                logger.debug('try delete a same name obj {} @{}'.format(same_obj.name, model))
                same_obj.delete_instance()
            else:
                return self.write_error(RespCode.APIFail, msg='Same name {} in {}'.format(same_obj.name, model))
        _obj = _MODELS[model].create(
            **{k: v for k, v in data.items() if not (k.endswith('_id') and data[k] == 0)})
        self.write_json(create_response(data=_obj.to_dict()))


class UDHandler(BaseHandler):
    @authenticated
    def post(self, model: str, pk: int):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        obj = _MODELS[model].select().where(_MODELS[model].id == pk).get()
        data = self.json_body
        if 'name' in data:
            if data['name'] != obj.name:
                return self.write_error(RespCode.APIFail, msg='创建之后禁止修改名字')

        for k, v in dict2underline(data).items():
            if k not in ('update_at', 'create_at', 'is_deleted', 'id') and not (k.endswith('_id') and v == 0):
                setattr(obj, k, v)
        obj.save()
        self.write_json(create_response(data=obj.to_dict()))

    @authenticated
    def delete(self, model: str, pk: int):
        if model not in _MODELS:
            return self.write_error(RespCode.APIFail)
        obj = _MODELS[model].select().where(_MODELS[model].id == pk).get()
        if obj is None:
            return self.write_error(RespCode.APIFail, msg='Object id {} not exist {}'.format(pk, model))
        obj.is_deleted = True
        obj.save()
        self.write_json(create_response(data=obj.to_dict()))


default_handlers = [
    (r'/api/count', APICounter),
    (r'/api/(?P<model>\w+)', CRHandler),
    (r'/api/(?P<model>\w+)/(?P<pk>\d+)', UDHandler),
]
