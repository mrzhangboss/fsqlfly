# -*- coding: utf-8 -*-
import re
import yaml
from typing import Optional
from collections import namedtuple
from io import StringIO
from typing import Callable, List, Tuple, Union, Any

__CAMEL_PATTERN = re.compile("(?<=[a-z0-9])(_[a-z])")


def str2camel(v: str) -> str:
    return __CAMEL_PATTERN.sub(lambda x: x.group()[1].upper(), v)


__UNDERLINE_PATTERN = re.compile("(?<=[a-z0-9])([A-Z])")


def str2underline(v: str) -> str:
    return v[0].lower() + __UNDERLINE_PATTERN.sub(lambda x: '_' + x.group().lower(), v[1:])


def _dict2_(value: Union[dict, list, str, int, float],
            method: Callable[[str], str]) -> Union[dict, list, str, int, float]:
    if isinstance(value, dict):
        return {method(k): _dict2_(v, method) for k, v in value.items()}
    elif isinstance(value, list):
        return [_dict2_(x, method) for x in value]
    else:
        return value


def dict2camel(v: dict) -> dict:
    return _dict2_(v, str2camel)


def dict2underline(v: dict) -> dict:
    return _dict2_(v, str2underline)


def _convert_yaml(source: Any, con: Callable) -> Any:
    if isinstance(source, dict):
        return {con(k): _convert_yaml(v, con) for k, v in source.items() if v is not None}
    elif isinstance(source, list):
        return [_convert_yaml(x, con) for x in source]
    else:
        return source


def load_yaml(source: str, to_underline: bool = True) -> dict:
    d = yaml.load(StringIO(source), Loader=yaml.SafeLoader)
    return _convert_yaml(d, lambda x: x.replace('-', '_') if to_underline else lambda x: x)


def dump_yaml(source: Union[list, dict], not_underline: bool = True) -> str:
    return yaml.dump(_convert_yaml(source, lambda x: x.replace('_', '-') if not_underline else lambda x: x))


def check_yaml(source: str) -> bool:
    try:
        load_yaml(source)
    except Exception as e:
        print(e)
        return False
    else:
        return True


def get_schema(source: str) -> dict:
    data = load_yaml(source)
    if 'schema' not in data:
        raise SystemError("Schema Not In Yaml file")
    return data['schema']


def get_sink_config(source: str) -> dict:
    return load_yaml(source)


def generate_yaml(source: List[Tuple[str, str]], is_sink: bool = False) -> str:
    schemas = []
    for t, d in source:
        if d == 'timestamp' and not is_sink:
            schemas.append({'name': 'rowTime', 'type': 'TIMESTAMP', 'rowtime': {'timestamps':
                                                                                    {'type': 'from-field',
                                                                                     'from': d},
                                                                                'watermarks': {
                                                                                    'type': 'periodic-bounded',
                                                                                    'delay': '6000'
                                                                                }}})
        else:
            schemas.append({'name': d, 'type': t})
    data = {
        'format': {
            'property-version': 1,
            'type': 'json',
            'schema': 'ROW<{}>'.format(', '.join(
                (x['name'] if 'rowtime' not in x else x['rowtime']['timestamps']['from']) + ' ' + x['type'] for x in
                schemas))
        },
        'schema': schemas
    }
    out = yaml.dump(data)
    return out


SqlProps = namedtuple('SqlProps', ['name', 'value'])

SQL_COMMENT_PATTERN = re.compile(r'/\*(.*?)(?=\*/)', re.DOTALL)
SQL_COMMENT_PATTERN_CLEAN = re.compile(r'/\*.*?(?=\*/)\*/', re.DOTALL)


def parse_sql(sql: str) -> List[SqlProps]:
    res = []
    for x in SQL_COMMENT_PATTERN.findall(sql):
        if '=' in x:
            k, v = map(str.strip, x.split('=', maxsplit=1))
            if v.startswith("'") or v.startswith('"'):
                v = v[1:-1]
            elif re.findall('\d+\.\d+', v):
                v = float(v)
            elif v.isdigit():
                v = int(v)
            res.append(SqlProps(k, v))
        else:
            res.append(SqlProps(x.strip(), True))
    return res


def clean_sql(sql: str) -> str:
    return SQL_COMMENT_PATTERN_CLEAN.sub('', sql).strip()


def get_job_header(transform, **kwargs) -> str:
    return "{}_{}{}".format(transform.id, transform.name, '.' + kwargs['pt'] if 'pt' in kwargs else '')


def get_job_short_name(transform) -> str:
    return "{}_{}".format(transform.id, transform.name)


def get_full_name(*args) -> str:
    return '.'.join([x for x in args if x])
