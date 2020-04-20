# -*- coding:utf-8 -*-
import attr
import re
import warnings
from fsqlfly.models import Resource, Namespace
from copy import deepcopy
import yaml
import logzero
from typing import List, Dict, Optional
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql.sqltypes import TypeDecorator
from typing import Optional, List, Type, Any
from re import _pattern_type


class BlinkSQLType:
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN'
    BYTES = 'BYTES'
    DECIMAL = 'DECIMAL'
    TINYINT = 'TINYINT'
    SMALLINT = 'SMALLINT'
    INTEGER = 'INTEGER'
    BIGINT = 'BIGINT'
    FLOAT = 'FLOAT'
    DOUBLE = 'DOUBLE'
    DATE = 'DATE'
    TIME = 'TIME'
    TIMESTAMP = 'TIMESTAMP'


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


@attr.s
class SchemaContent:
    name: str = attr.ib()
    type: str = attr.ib()
    database: Optional[str] = attr.ib(default=None)
    comment: Optional[str] = attr.ib(default=None)
    primary_key: Optional[str] = attr.ib(default=None)
    fields: List[SchemaField] = attr.ib(factory=list)
    partitionable: bool = attr.ib(default=False)


class DatabaseManager(object):
    use_comment = True
    use_primary = True

    def __init__(self, connection_url: str, table_name_filter: NameFilter, db_type='mysql'):
        self.connection_url = connection_url
        self.need_tables = table_name_filter
        self.db_type = db_type

    def _get_flink_type(self, typ: TypeDecorator) -> Optional[str]:
        from sqlalchemy.dialects.mysql.types import _StringType as M_STRING, BIT as M_BIT, TINYINT, DOUBLE as M_DOUBLE
        from sqlalchemy.dialects.postgresql import (DOUBLE_PRECISION as P_DOUBLE, BIT as P_BIT, VARCHAR, CHAR, TEXT,
                                                    JSON, BOOLEAN)
        from sqlalchemy.sql.sqltypes import (DATE, _Binary, INTEGER, SMALLINT, BIGINT, FLOAT, DECIMAL,
                                             DATETIME,
                                             TIMESTAMP, TIME)
        name = None
        types = BlinkSQLType
        if isinstance(typ, (M_STRING, VARCHAR, CHAR, TEXT, JSON)):
            name = types.STRING
        elif isinstance(typ, _Binary):
            name = types.BYTES
        elif isinstance(typ, BOOLEAN):
            name = types.BOOLEAN
        elif isinstance(typ, TINYINT):
            name = types.TINYINT
        elif isinstance(typ, SMALLINT):
            name = types.SMALLINT
        elif isinstance(typ, (P_BIT, M_BIT)):
            name = types.TINYINT
        elif isinstance(typ, INTEGER):
            name = types.INTEGER
        elif isinstance(typ, BIGINT):
            name = types.BIGINT
        elif isinstance(typ, FLOAT):
            name = types.FLOAT
        elif isinstance(typ, (M_DOUBLE, P_DOUBLE)):
            name = types.DOUBLE
        elif isinstance(typ, DECIMAL):
            name = "{}({},{})".format(types.DECIMAL, typ.precision, typ.scale)
        elif isinstance(typ, DATETIME) or isinstance(typ, TIMESTAMP):
            name = types.TIMESTAMP
        elif isinstance(typ, DATE):
            name = types.DATE
        elif isinstance(typ, TIME):
            name = types.TIME

        if name is None:
            logzero.logger.error("Not Support Current Type in DB {}".format(str(typ)))
            return None
        return name

    def update(self):
        from sqlalchemy.sql.sqltypes import INTEGER, SMALLINT, BIGINT
        engine = create_engine(self.connection_url)
        insp = inspect(engine)
        db_list = insp.get_schema_names()
        update_tables = []
        for db in db_list:
            for tb in insp.get_table_names(db):
                full_name = f'{db}.{tb}'
                if full_name in self.need_tables:
                    update_tables.append((db, tb))

        schemas = []

        for db, tb in update_tables:
            comment = insp.get_table_comment(table_name=tb, schema=db)['text'] if self.use_comment else None
            schema = SchemaContent(name=tb, database=db, comment=comment, type=self.db_type)
            columns = insp.get_columns(table_name=tb, schema=db)
            primary = insp.get_primary_keys(tb, db) if self.use_primary else None
            if primary and len(primary) == 1:
                schema.primary_key = primary[0]
                column = list(filter(lambda x: x['name'] == primary[0], columns))[0]
                if isinstance(column['type'], (INTEGER, SMALLINT, BIGINT)):
                    schema.partitionable = True

            fields = []
            for x in columns:
                field = SchemaField(name=x['name'], type=self._get_flink_type(x['type']),
                                    nullable=x['nullable'], autoincrement=x.get('autoincrement'))
                if field.type is None:
                    logzero.logger.error(
                        "Not Add Column {} in {}.{} current not support : {}".format(field.name, schema.database,
                                                                                     schema.name, str(x['type'])))
                else:
                    fields.append(field)

            fields.sort(key=lambda x: x.name)

            schema.fields.extend(fields)

            print(schema)
            schemas.append(schema)

        return schemas


class HiveManager(DatabaseManager):
    use_comment = False
    use_primary = False

    hive_types = set(list(x for x in dir(BlinkHiveSQLType) if not x.startswith('__')))

    def __init__(self, connection_url: str, table_name_filter: NameFilter):
        super(HiveManager, self).__init__(connection_url, table_name_filter, 'hive')

    def _get_flink_type(self, typ: TypeDecorator) -> Optional[str]:
        from sqlalchemy.sql.sqltypes import (DATE, _Binary, TIME, VARCHAR, String, CHAR, BINARY)

        name = None
        types = BlinkHiveSQLType
        str_name = str(typ)


        if isinstance(typ, (VARCHAR, CHAR, String)):
            name = types.STRING
        elif isinstance(typ, BINARY):
            name = types.BYTES
        elif str_name in self.hive_types:
            name = str_name
        if name is None:
            logzero.logger.error("Not Support Current Type in DB {}".format(str(typ)))
            return None
        return name
