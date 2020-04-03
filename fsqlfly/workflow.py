# -*- coding: utf-8 -*-
import os
import re
import subprocess
import tempfile
import yaml
from typing import Optional
from jinja2 import Template
from terminado.management import NamedTermManager
from fsqlfly.settings import FSQLFLY_UPLOAD_DIR, FSQLFLY_FLINK_BIN, logger
from fsqlfly.models import Transform, Namespace, Resource, Functions
from fsqlfly import settings


def _create_config_from_resource(resource: Resource, **kwargs) -> dict:
    data = yaml.load(handle_template(resource.yaml, **kwargs), yaml.FullLoader)
    data['name'] = resource.name
    return data


def _get_functions() -> list:
    res = []
    for f in Functions.select().where(Functions.is_deleted == False).objects():
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
    for f in Functions.select().where(Functions.is_deleted == False).objects():
        r_p = os.path.join(FSQLFLY_UPLOAD_DIR, f.resource.real_path[1:])
        res.append(r_p)

    out = []
    for x in set(res):
        out.extend(['-j', x])
    return out


def _create_config(require: str, config: Optional[str], **kwargs) -> str:
    tables = []
    if require.strip():
        for x in require.split(','):
            if '.' in x:
                space, name = x.split('.', 1)
            else:
                space, name = None, x

            if space:
                space = Namespace.select().where(Namespace.name == space).first()

            resource = Resource.select().where(Namespace.name == name & Resource.namespace == space).first()
            resource_only_name = Resource.select().where(Resource.name == name).first()
            if resource is None and resource_only_name is not None:
                resource = resource_only_name

            data = _create_config_from_resource(resource, **kwargs)
            tables.append(data)
    base_config = yaml.load(handle_template(config, **kwargs), yaml.FullLoader) if config else dict()
    if base_config is None:
        base_config = dict()
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

    yaml_conf = _create_config(transform.require, transform.yaml, **kwargs)
    sql = handle_template(transform.sql, **kwargs)
    print(yaml_conf, file=open(yaml_f, 'w'))
    print(sql, file=open(sql_f, 'w'))
    print('q\nexit;', file=open(sql_f, 'a+'))
    pt = '_' + kwargs['pt'] if 'pt' in kwargs else ''
    run_commands = [FSQLFLY_FLINK_BIN, 'embedded',
                    '-s', '{}_{}.{}-'.format(transform.id, transform.name, pt),
                    '--environment', yaml_f,
                    *_get_jar(),
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

    os.remove(yaml_f)
    os.remove(sql_f)

    print(out_w, file=open('out.shell.txt', 'w'))
    print(out_w)
    return True, out_w


def run_debug_transform(data: dict, manager: NamedTermManager) -> (str, str):
    _, yaml_f = tempfile.mkstemp(suffix='.yaml')
    yaml_conf = _create_config(data.get('require', ''), data.get('yaml', ''))
    print(yaml_conf, file=open(yaml_f, 'w'))
    real_sql = handle_template(data.get('sql', ''))
    name = manager._next_available_name()
    run_commands = [FSQLFLY_FLINK_BIN, 'embedded',
                    '-s', '{}{}.'.format(settings.TEMP_TERMINAL_HEAD, str(name)),
                    '--environment', yaml_f,
                    *_get_jar()]
    logger.debug('running commands is : {}'.format(' '.join(run_commands)))
    term = manager.new_terminal(shell_command=run_commands)

    logger.debug('sql :{}'.format(real_sql))
    term.ptyproc.write(real_sql)
    term.term_name = name
    setattr(term, settings.TERMINAL_OPEN_NAME, True)
    term.run_command = ' '.join(run_commands)
    manager.terminals[name] = term
    return name
