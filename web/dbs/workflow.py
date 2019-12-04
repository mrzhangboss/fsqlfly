# -*- coding: utf-8 -*-
import json
import os
import re
import subprocess
import tempfile
import yaml
from typing import Optional
from io import StringIO
from urllib.parse import urlparse
from jinja2 import Template
from web.settings import BASE_DIR, FLINK_BIN_PATH
from .models import Transform, Namespace, Resource, Functions


def _create_config_from_resource(resource: Resource, **kwargs) -> dict:
    data = yaml.load(handle_template(resource.yaml, **kwargs), yaml.FullLoader)
    data['name'] = resource.name
    return data


def _get_functions() -> list:
    res = []
    for f in Functions.objects.filter(is_deleted=False).all():
        fc = {
            'name': f.name,
            'from': f.function_from,
            'class': f.class_name
        }
        if f.constructor_config.strip():
            fc['constructor'] = yaml.load(f.constructor_config, yaml.FullLoader)
        res.append(fc)
    return res


def _get_jar() -> str:
    res = []
    for f in Functions.objects.filter(is_deleted=False).all():
        res.append(os.path.join(BASE_DIR, f.resource.real_path)[1:])
    return ' '.join('-j {} '.format(x) for x in res)


def _create_config(require: dict, config: Optional[str], **kwargs) -> str:
    tables = []
    for r in require:
        rid = r['id']
        resource = Resource.objects.get(id=rid)
        data = _create_config_from_resource(resource, **kwargs)
        tables.append(data)
    base_config = yaml.load(handle_template(config, **kwargs), yaml.FullLoader) if config else dict()
    if base_config.get('tables'):
        base_config['tables'].extend(tables)
    else:
        base_config['tables'] = tables
    base_config['functions'] = _get_functions()
    return yaml.dump(base_config)


def _clean(s: str) -> str:
    return re.sub(r'\[\d+(;\d+)?m?', '', s)


def handle_template(text: str, **kwargs) -> str:
    return Template(text).render(**kwargs)


def run_transform(transform: Transform, **kwargs) -> (bool, str):
    _, yaml_f = tempfile.mkstemp(suffix='.yaml')
    _, sql_f = tempfile.mkstemp(suffix='.sql')

    yaml_conf = _create_config(json.loads(transform.require), transform.yaml, **kwargs)
    sql = handle_template(transform.sql, **kwargs)
    print(yaml_conf, file=open(yaml_f, 'w'))
    print(sql, file=open(sql_f, 'w'))
    print('q\nexit;', file=open(sql_f, 'a+'))
    pt = '' if 'pt' in kwargs else '_' + kwargs['pt']
    run_commands = [FLINK_BIN_PATH, 'embedded',
                    '-s', '{}_{}{}'.format(transform.id, transform.name, pt),
                    '--environment', yaml_f,
                    _get_jar(),
                    '<', sql_f]
    print(' '.join(run_commands))
    try:
        out = subprocess.check_output(' '.join(run_commands), shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        return False, "sql:\n {} \n\noutput: \n{} \n\n error: {}\n\nyaml: \n{}".format(transform.sql,
                                                                                       error.stdout.decode(),
                                                                                       error.stderr.decode(),
                                                                                       yaml_conf)
    except Exception as e:
        print(e)
        return False, str(e)

    out_w = _clean(out.decode())
    print(out_w, file=open('out.shell.txt', 'w'))
    print(out_w)
    return True, out_w


def run_debug_transform(data: dict) -> (str, str):
    _, yaml_f = tempfile.mkstemp(suffix='.yaml')
    _, sql_f = tempfile.mkstemp(suffix='.sql')
    yaml_conf = _create_config(data['columns'], data['config'])
    print(yaml_conf, file=open(yaml_f, 'w'))
    print(handle_template(data['sql']), file=open(sql_f, 'w'))
    run_commands = [FLINK_BIN_PATH, 'embedded',
                    '-s', '{}_{}'.format(data.get('id', 'null'), "{}"),
                    '--environment', yaml_f,
                    _get_jar()]

    return ' '.join(run_commands), sql_f
