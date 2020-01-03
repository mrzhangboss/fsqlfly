import os
import json
import pickle
from typing import Optional, Union
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.db.models import Model

from django.views.decorators.http import require_http_methods
from django.core import serializers
from utils.strings import dict2camel, dict2underline
from web.settings import BASE_DIR
from tempfile import mkstemp
from dbs.models import Namespace, FileResource, Functions, Transform, Resource, Relationship, Connection
from utils.response import create_response
from utils.strings import check_yaml
from utils.db_crawler import Crawler

example = create_response()
support_upload = ['logo', 'file']
basic_upload_file = os.path.join(BASE_DIR, 'upload')
upload_dirs = {x: os.path.join(basic_upload_file, x) for x in support_upload}
_ = [os.makedirs(x, exist_ok=True) for x in upload_dirs.values()]


def check_dict_yaml(data: dict):
    for k in ['sinkSchema', 'sink_schema', 'yaml', 'constructor']:
        if k in data:
            check_yaml(data[k])


def count_view(req: HttpRequest) -> JsonResponse:
    data = {
        "namespaceNum": Namespace.objects.filter(is_deleted=False).count(),
        "resourceNum": Resource.objects.filter(is_deleted=False).count(),
        "functionNum": Functions.objects.filter(is_deleted=False).count(),
        "fileNum": FileResource.objects.filter(is_deleted=False).count(),
    }
    return JsonResponse(data)


@require_http_methods(['POST'])
def upload(req: HttpRequest) -> JsonResponse:
    if len(req.FILES.keys()) != 1:
        raise SystemError("Not support upload too many file")
    key = list(req.FILES.keys())[0]
    if key not in support_upload:
        raise SystemError("Not support upload tag")
    upload_file = req.FILES[key]

    _, tem_f = mkstemp(suffix=upload_file.name, dir=upload_dirs[key])
    with open(tem_f, 'wb+') as out:
        for chunk in upload_file.chunks():
            out.write(chunk)
    real_path = '/upload/' + key + '/' + os.path.basename(tem_f)
    return create_response(data={"realPath": real_path})


def current_user(req: HttpRequest) -> JsonResponse:
    return JsonResponse(data={"name": req.user.username,
                              "avatar": 'https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png'})


_MODELS = {
    'functions': Functions,
    'namespace': Namespace,
    'resource': Resource,
    'transform': Transform,
    'file': FileResource,
    'relationship': Relationship,
    'connection': Connection,
}

NOT_USED_FIELD = ['is_deleted', 'create_by', 'cache']


def serialize_model_fields(_obj: Model, not_used=None) -> dict:
    if hasattr(_obj, 'cache'):
        cache_back = getattr(_obj, 'cache')
        _obj.cache = None
    if not_used is None:
        not_used = NOT_USED_FIELD
    model_ = json.loads(
        serializers.serialize('json', [_obj, ], use_natural_foreign_keys=True, use_natural_primary_keys=True))[0]
    if hasattr(_obj, 'cache'):
        _obj.cache = cache_back

    return dict(id=model_['pk'],
                **{k if k != 'namespace' else k + '_id': v for k, v in model_['fields'].items() if k not in not_used})


# Create your views here.
def create_or_get_list(req: HttpRequest, model: str) -> JsonResponse:
    if req.method == 'POST':
        data = dict2underline(json.loads(req.body))
        check_dict_yaml(data)
        try:
            _obj = _MODELS[model].objects.create(
                **{k: v for k, v in data.items() if not (k.endswith('_id') and data[k] == 0)})
            return create_response(data=dict2camel(serialize_model_fields(_obj)))
        except Exception as e:
            return create_response(code=500, msg=str(e))
    else:
        res = []
        for obj in _MODELS[model].objects.filter(is_deleted=False).all():
            res.append(serialize_model_fields(obj))
        return create_response(data=[dict2camel(x) for x in res])


def update_or_delete(req: HttpRequest, model: str, pk: int) -> JsonResponse:
    obj = _MODELS[model].objects.get(id=pk)
    res = example
    if req.method == 'DELETE':
        obj.is_deleted = True
    else:
        data = dict2underline(json.loads(req.body))
        check_dict_yaml(data)
        for k in data:
            if k not in ['create_at', 'update_at']:
                value = None if k.endswith('_id') and data[k] == 0 else data[k]
                setattr(obj, k, value)
        res = create_response(data=dict2camel(serialize_model_fields(obj)))
    obj.save()
    return res


def run_model_command(req: HttpRequest, model: str, method: str, pk: int) -> JsonResponse:
    if method == 'update':
        if model == 'relationship':
            relation = Relationship.objects.get(pk=pk)
            relation.save()
        if model == 'connection':
            crawler = Crawler()
            con = Connection.objects.get(pk=pk)
            cache = crawler.get_cache(con.url, con.suffix, con.typ, con.name, con.table_regex, con.table_exclude_regex)
            if cache is not None:
                con.cache = pickle.dumps(cache)
                con.save()
                updated = True
    return create_response()
