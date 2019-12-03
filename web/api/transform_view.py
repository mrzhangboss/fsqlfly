# -*- coding: utf-8 -*-
import os
import json
import random
from datetime import datetime
from base64 import b64decode, b64encode
from typing import Optional, Union
from urllib.parse import quote
import yaml
from django.db.models import Model
from django.http import HttpRequest, JsonResponse
from django.core.cache import caches, cache
from dbs.models import Namespace, FileResource, Functions, Transform, Resource
from utils.response import create_response
from utils.strings import check_yaml, dict2underline, get_schema, get_sink_config
from dbs.workflow import run_transform, run_debug_transform
from web.settings import TERMINAL_WEB_HOST_FMT


def get_row_proc_columns_from_yaml(s: str) -> tuple:
    # todo: parse rowtime and proctime
    rowtime, proctime, columns = '', '', []
    schema = get_schema(s)
    for sc in schema:
        if sc['type'] in ['DATE', 'TIMESTAMP', 'TIME']:
            columns.append(sc)
        if 'rowtime' in sc:
            rowtime = sc['name']
        if 'proctime' in sc:
            proctime = sc['name']

    return rowtime, proctime, columns


def random_name(prefix='auto_generate'):
    rid = random.randint(100000, 999999)
    first = Transform.objects.order_by('-id').first()
    fid = first.id + 1 if first else 0
    return f'{prefix}_{fid}_{rid}'


def init_sink(transform_name: str, model: Optional[Resource], sink_yaml, namespace: Optional[Model] = None) -> Model:
    config = get_sink_config(sink_yaml)
    name = config['name'] if 'name' in config else transform_name
    if 'format' not in config:
        config['format'] = {'property-version': 1, 'type': 'json', 'derive-schema': True}

    new_yaml = yaml.dump(config)
    if model is None:
        model = Resource.objects.create(name=name, info='auto generate {}'.format(datetime.now()),
                                        yaml=new_yaml, namespace=namespace, typ='sink-table')
    else:
        model.name = name
        model.yaml = new_yaml
        model.namespace = namespace
        model.save()
    return model


def get_info(req: HttpRequest) -> JsonResponse:
    namespaces = [{'name': x.name, 'id': x.id} for x in Namespace.objects.filter(is_deleted=False).all()]
    sources = []
    ids = Resource.objects.filter(is_deleted=False).values('id')
    for sou in ids:
        cache_name = '{}:resource:cache'.format(sou['id'])
        if cache.get(cache_name) is not None:
            sources.append(caches[cache_name])
        else:
            sou = Resource.objects.get(pk=sou['id'])
            row_time, proc_time, columns = get_row_proc_columns_from_yaml(sou.yaml)
            data = {
                'id': sou.id,
                'name': sou.name,
                'namespaceId': sou.namespace.id if sou.namespace else 0,
                'namespace': sou.namespace.name if sou.namespace else 'DEFAULT',
                'info': sou.info,
                'rowtime': row_time,
                'proctime': proc_time,
                'disabled': not sou.is_available,
                'avatar': sou.namespace.avatar if sou.namespace else '',
                'columns': columns,
            }
            sources.append(data)
            cache.set(cache_name, data)

    return create_response(data={'namespaces': namespaces, 'columns': sources})


def get_list_or_create(req: HttpRequest) -> JsonResponse:
    if req.method == 'POST':
        data = json.loads(req.body)
        namespace = Namespace.objects.get(id=data['namespaceId']) if data['namespaceId'] else None
        obj = Transform.objects.create(name=data['name'], info=data['info'],
                                       sql=data['sql'], require=json.dumps(data['columns']),
                                       yaml=data['config'], namespace=namespace, is_publish=data['isPublish'],
                                       is_available=data['isAvailable'])
        return create_response(data={'id': obj.id, 'namespaceId': obj.namespace.id if obj.namespace else 0})
    res = []
    for sou in Transform.objects.filter(is_deleted=False).all():
        res.append({
            'id': sou.id,
            'name': sou.name,
            'namespaceId': sou.namespace.id if sou.namespace else 0,
            'info': sou.info,
            'isAvailable': sou.is_available,
            'isPublish': sou.is_publish,
            'createAt': str(sou.create_at),
            'updateAt': str(sou.update_at),
        })
    return create_response(data=res)


def debug_transform(req: HttpRequest) -> JsonResponse:
    data = json.loads(req.body)
    print(data)
    command, file_name = run_debug_transform(data)
    encode_file_name = quote(file_name)
    url = TERMINAL_WEB_HOST_FMT.format(b64encode(command.encode()).decode(), encode_file_name)
    return create_response(data={"url": url})


def start_run(req: HttpRequest, pk: int) -> JsonResponse:
    obj = Transform.objects.get(pk=pk)
    success, out = run_transform(obj)
    return create_response(msg=out, code=0 if success else 500)


def get_or_update_or_delete(req: HttpRequest, pk: int) -> JsonResponse:
    obj = Transform.objects.get(pk=pk)
    if req.method == 'GET':
        return create_response(data={
            'detail': {
                'sql': obj.sql,
                'config': '' if obj.yaml is None else obj.yaml
            },
            'resources': {
                'columns': json.loads(obj.require)
            }
        })
    elif req.method == 'DELETE':
        obj.is_deleted = True
        obj.save()
    else:
        data = json.loads(req.body)
        obj.name = data['name']
        obj.info = data['info']
        obj.is_available = data['isAvailable']
        obj.is_publish = data['isPublish']
        obj.require = json.dumps(data['columns'])
        namespace = Namespace.objects.get(id=data['namespaceId']) if data['namespaceId'] else None
        obj.namespace = namespace
        obj.sql = data['sql']
        assert check_yaml(data['config'])
        obj.yaml = data['config']
        obj.save()
    return create_response(data={'id': obj.id, 'namespaceId': obj.namespace.id if obj.namespace else 0})
