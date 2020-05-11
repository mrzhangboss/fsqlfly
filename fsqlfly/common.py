# -*- coding:utf-8 -*-
import re
import functools
import urllib
import traceback
import attr
from urllib.parse import urlencode
from re import _pattern_type
from typing import Any, Optional, NamedTuple, Callable, Awaitable, Union, List, Type
from tornado.web import RequestHandler, HTTPError
from logzero import logger

SUPPORT_TABLE_TYPE = {'sink', 'source', 'both', 'view', 'temporal-table'}
SUPPORT_MANAGER = {'hive', 'db', 'kafka', 'hbase', 'elasticsearch', 'file'}
CONNECTOR_TYPE = {'canal', 'system'}


class CodeMsg(NamedTuple):
    code: int
    msg: str


class RespCode:
    Success = CodeMsg(200, 'Success')
    ServerError = CodeMsg(500, 'Web Server Error')
    NeedLogin = CodeMsg(503, 'You Need Login')
    LoginFail = CodeMsg(501, 'Wrong Password or Token')
    APIFail = CodeMsg(502, 'Invalid API Request')
    InvalidHttpMethod = CodeMsg(405, 'Invalid HTTP method.')


@attr.s
class DBRes:
    data: Any = attr.ib(default=None)
    code: int = attr.ib(default=200)
    msg: Optional[str] = attr.ib(default=None)
    success: bool = attr.ib()

    @success.default
    def get_success(self):
        return self.code == 200

    @classmethod
    def login_error(cls, msg: str = RespCode.LoginFail.code):
        return DBRes(code=RespCode.LoginFail.code, msg=msg)

    @classmethod
    def api_error(cls, msg: str = RespCode.APIFail.msg):
        return DBRes(code=RespCode.APIFail.code, msg=msg)

    @classmethod
    def not_found(cls, msg: str = "Can't found Object"):
        return DBRes(code=RespCode.APIFail.code, msg=msg)

    @classmethod
    def resource_locked(cls, msg: str = "Resource Locked"):
        return DBRes(code=RespCode.APIFail.code, msg=msg)

    @classmethod
    def sever_error(cls, msg: str = RespCode.ServerError.msg):
        return DBRes(code=RespCode.ServerError.code, msg=msg)


def safe_authenticated(
        method: Callable[..., Optional[Awaitable[None]]]
) -> Callable[..., Union[Optional[Awaitable[None]], DBRes]]:
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """

    @functools.wraps(method)
    def wrapper(  # type: ignore
            self: RequestHandler, *args, **kwargs
    ) -> Union[Optional[Awaitable[None]], DBRes]:
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urllib.parse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        assert self.request.uri is not None
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return None
            raise HTTPError(403)
        from fsqlfly import settings
        if settings.FSQLFLY_DEBUG:
            return method(self, *args, **kwargs)
        try:
            return method(self, *args, **kwargs)
        except Exception:
            err = traceback.format_exc()
            logger.error(err)
            return DBRes.sever_error(msg=f'meet {err}')

    return wrapper


class NameFilter:
    @classmethod
    def get_pattern(cls, s: str) -> List[Type[_pattern_type]]:
        s = s.replace('，', ',')
        patterns = [s.strip()] if ',' not in s else s.split(',')
        res = [re.compile(pattern=x + '$') for x in patterns]
        return res

    def __init__(self, include: str = '', exclude: str = ''):
        self.includes = self.get_pattern(include) if include else [re.compile(r'.*')]
        self.excludes = self.get_pattern(exclude) if exclude else []

    def __contains__(self, item: str) -> bool:
        if any(map(lambda x: x.match(item) is not None, self.includes)):
            if self.excludes and any(map(lambda x: x.match(item), self.excludes)):
                return False
            return True
        return False


@attr.s
class SchemaField:
    name: str = attr.ib()
    type: str = attr.ib()
    comment: Optional[str] = attr.ib(default=None)
    nullable: Optional[bool] = attr.ib(default=True)
    autoincrement: Optional[bool] = attr.ib(default=None)
    rowtime: Optional[Any] = attr.ib(default=None)
    proctime: Optional[bool] = attr.ib(default=None)


@attr.s
class SchemaContent:
    name: str = attr.ib()
    type: str = attr.ib()
    database: Optional[str] = attr.ib(default=None)
    comment: Optional[str] = attr.ib(default=None)
    primary_key: Optional[str] = attr.ib(default=None)
    fields: List[SchemaField] = attr.ib(factory=list)
    partitionable: bool = attr.ib(default=False)


@attr.s
class VersionConfig:
    exclude: Optional[str] = attr.ib(default=None)
    include: Optional[str] = attr.ib(default=None)
    update_mode: Optional[str] = attr.ib(default=None)
    query: Optional[str] = attr.ib(default=None)
    history_table: Optional[str] = attr.ib(default=None)
    primary_key: Optional[str] = attr.ib(default=None)
    time_attribute: Optional[str] = attr.ib(default=None)
    format: Optional[Any] = attr.ib(default=None)
    schema: list = attr.ib(factory=list)


class BlinkSQLType:
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN'
    BYTES = 'BYTES'
    DECIMAL = 'DECIMAL(38,18)'
    TINYINT = 'TINYINT'
    SMALLINT = 'SMALLINT'
    INTEGER = 'INTEGER'
    BIGINT = 'BIGINT'
    FLOAT = 'FLOAT'
    DOUBLE = 'DOUBLE'
    DATE = 'DATE'
    TIME = 'TIME'
    TIMESTAMP = 'TIMESTAMP(3)'


class BlinkHiveSQLType(BlinkSQLType):
    INTERVAL = 'INTERVAL'
    ARRAY = 'ARRAY'
    MULTISET = 'MULTISET'
    MAP = 'MAP'
    RAW = 'RAW'


class BlinkTableType:
    sink = 'sink'
    source = 'source'
    both = 'both'


class DBSupportType:
    MySQL = 'MySQL'
    PostgreSQL = 'PostgreSQL'


class CanalMode:
    upsert = 'upsert'
    update = 'update'
    insert = 'insert'
    delete = 'delete'
    all = 'all'

    @classmethod
    def support_modes(cls) -> set:
        return {cls.upsert, cls.insert, cls.update, cls.delete}

    def __contains__(self, item) -> bool:
        return item in self.support_modes

    def __init__(self, config_mode: str):
        if CanalMode.all in config_mode:
            mode = [CanalMode.update, CanalMode.insert, CanalMode.delete]
        else:
            mode = config_mode.split(',')
        all_mode_support = all(map(lambda x: x in CANAL_MODE, mode))
        assert all_mode_support, 'Canal Config not support mode {}'.format(mode)
        if CanalMode.upsert in mode:
            assert len(mode) == 1, 'upsert only support run by itself'
        self._mode = mode

    def is_upsert(self):
        return self.upsert in self._mode

    def is_support(self, mode: str) -> bool:
        if self.is_upsert():
            return True
        return mode in self._mode

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self._mode):
            raise StopIteration
        v = self._mode[self._i]
        self._i += 1
        return v


CANAL_MODE = CanalMode.support_modes()

DEFAULT_CONFIG = """
[db]
insert_primary_key = false
add_read_partition_key = false
read_partition_key = id
read_partition_fetch_size = 100
read_partition_lower_bound = 0
read_partition_upper_bound = 50000
read_partition_num = 50

[kafka]
process_time_enable = true
process_time_name = flink_process_time
rowtime_enable = true
rowtime_from = MYSQL_DB_EXECUTE_TIME

[hive]

example = 1

[canal]
mode = upsert
process_time_enable = true
process_time_name = flink_process_time
rowtime_enable = true
rowtime_name = mysql_row_time
rowtime_watermarks = 5000
rowtime_from = MYSQL_DB_EXECUTE_TIME
binlog_type_name = MYSQL_DB_EVENT_TYPE
before_column_suffix = _before
after_column_suffix = _after
update_suffix = _updated
table_filter = .*\..*

[system]
source_include: .*
source_exclude: ''
target_database_format: {{ resource_name.database }}
target_table_format: {{ resource_name.name }}
transform_name_format: {{ source_type }}2{{ target_type }}__{{ connector.name }}__{{ resource_name.database }}__{{ resource_name.name }}  
use_partition: false
partition_name: pt
partition_value: {{ ds_nodash }}

"""
