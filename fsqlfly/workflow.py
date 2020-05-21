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
from fsqlfly.db_helper import Transform, DBDao
from fsqlfly import settings
from fsqlfly.utils.strings import get_job_header, dump_yaml
from fsqlfly.utils.template import generate_template_context


def _create_config(require: str, config: Optional[str], args: dict) -> str:
    tables = []
    catalogs = []
    require = require.strip() if require and require.strip() else ''
    if require:
        tables.extend(DBDao.get_require_table(require))
        catalogs.extend(DBDao.get_require_catalog(require))

    base_config = yaml.load(handle_template(config, args), yaml.FullLoader) if config else dict()
    if base_config is None:
        base_config = dict()
    if base_config.get('tables'):
        base_config['tables'].extend(tables)
    else:
        base_config['tables'] = tables
    base_config['functions'] = DBDao.get_require_functions()
    if base_config.get('catalogs'):
        base_config['catalogs'].extend(catalogs)
    else:
        base_config['catalogs'] = catalogs
    return dump_yaml(base_config)


def _clean(s: str) -> str:
    return re.sub(r'\[\d+(;\d+)?m?', '', s)


def handle_template(text: Optional[str], args: dict) -> str:
    return Template(text).render(**generate_template_context(**args)) if text else ''


def run_transform(transform: Transform, **kwargs) -> (bool, str):
    _, yaml_f = tempfile.mkstemp(suffix='.yaml')
    _, sql_f = tempfile.mkstemp(suffix='.sql')

    yaml_conf = _create_config(require=transform.require, config=transform.yaml, args=kwargs)
    sql = handle_template(transform.sql, kwargs)
    print(yaml_conf, file=open(yaml_f, 'w'))
    print(sql, file=open(sql_f, 'w'))
    print('q\nexit;', file=open(sql_f, 'a+'))
    run_commands = [FSQLFLY_FLINK_BIN, 'embedded',
                    '-s', get_job_header(transform, **kwargs),
                    '--environment', yaml_f,
                    *DBDao.get_require_jar(),
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
    yaml_conf = _create_config(data.get('require', ''), data.get('yaml', ''), dict())
    print(yaml_conf, file=open(yaml_f, 'w'))
    real_sql = handle_template(data.get('sql', ''), dict())
    name = manager._next_available_name()
    run_commands = [FSQLFLY_FLINK_BIN, 'embedded',
                    '-s', '{}{}'.format(settings.TEMP_TERMINAL_HEAD, str(name)),
                    '--environment', yaml_f,
                    *DBDao.get_require_jar()]
    logger.debug('running commands is : {}'.format(' '.join(run_commands)))
    term = manager.new_terminal(shell_command=run_commands)

    logger.debug('sql :{}'.format(real_sql))
    term.ptyproc.write(real_sql)
    term.term_name = name
    setattr(term, settings.TERMINAL_OPEN_NAME, True)
    term.run_command = ' '.join(run_commands)
    manager.terminals[name] = term
    return name
