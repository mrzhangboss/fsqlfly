# -*- coding:utf-8 -*-
import attr
import warnings
from typing import List, Union, Any, Optional
from copy import deepcopy
from collections import defaultdict
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.engine import Engine
from sqlalchemy.engine.result import ResultProxy
from sqlalchemy.types import TypeDecorator
from sqlalchemy import exc as sa_exc

@attr.s
class ColumnInfo:
    name: str = attr.ib()
    type: TypeDecorator = attr.ib()
    default: Optional[Any] = attr.ib()
    nullable: bool = attr.ib()
    comment: Optional[str] = attr.ib(default=None)
    autoincrement: bool = attr.ib(default=False)


@attr.s(auto_attribs=True)
class ForeignKey:
    name: str = attr.ib()
    referred_schema: Optional[str] = attr.ib()
    referred_table: str = attr.ib()
    options: dict = attr.ib()
    constrained_columns: List[str] = attr.Factory(list)
    referred_columns: List[str] = attr.Factory(list)


@attr.s(auto_attribs=True)
class UniqueKey:
    name: str = attr.ib()
    duplicates_index: str = attr.ib()
    column_names: List[str] = attr.Factory(list)


@attr.s(auto_attribs=True)
class IndexKey:
    name: str = attr.ib()
    unique: bool = attr.ib()
    dialect_options: Optional[dict] = attr.ib(default=None)
    type: Optional[str] = attr.ib(default=None)
    column_names: List[str] = attr.Factory(list)


@attr.s(auto_attribs=True)
class TableInfo:
    name: str = attr.ib()
    database: str = attr.ib()
    comment: Optional[str] = attr.ib()
    columns: List[ColumnInfo] = attr.Factory(list)
    foreign_keys: List[ForeignKey] = attr.Factory(list)
    unique_keys: List[UniqueKey] = attr.Factory(list)
    indexes: List[IndexKey] = attr.Factory(list)
    primary_keys: List[str] = attr.Factory(list)


@attr.s(auto_attribs=True)
class TableCache:
    suffix: str = attr.ib()
    tables: List[TableInfo] = attr.Factory(list)
    databases: List[str] = attr.Factory(list)


class Crawler:
    @classmethod
    def execute_sql(cls, engine: Engine, sql: str) -> list:
        with engine.connect() as connection:
            return connection.execute(sql).fetchall()

    @classmethod
    def get_all_database(cls, engine: Engine):
        filter_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
        return [x[0] for x in cls.execute_sql(engine, 'show databases') if x[0] not in filter_dbs]

    def get_cache(self, connection_url: str, suffix: str, typ: str) -> TableCache:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=sa_exc.SAWarning)
            warnings.filterwarnings("ignore", category=ImportWarning)
            if typ in {'mysql', 'hive'}:
                return self.get_db_cache(connection_url, suffix, typ)
            raise NotImplementedError("Not Support Generate {} Cache".format(typ))

    def get_db_cache(self, connection_url: str, suffix: str, typ: str) -> TableCache:
        url = make_url(connection_url)

        engine = create_engine(url)
        databases = self.get_all_database(engine)
        cache = TableCache(suffix=suffix)
        insp = inspect(engine)
        cache.databases = databases
        for db in databases:

            table_names = set(insp.get_table_names(db))
            for n in table_names:
                t_comment = insp.get_table_comment(n, db)['text'] if typ == 'mysql' else None
                columns = [ColumnInfo(**x) for x in insp.get_columns(n, db)]
                foreign_keys = [ForeignKey(**x) for x in insp.get_foreign_keys(n, db)] if typ == 'mysql' else []
                unique_keys = [UniqueKey(**x) for x in insp.get_unique_constraints(n, db)]  if typ == 'mysql' else []
                indexes = [IndexKey(**x) for x in insp.get_indexes(n, db)]
                primary_keys = insp.get_primary_keys(n, db) if typ == 'mysql' else []
                table_info = TableInfo(name=n, database=db, columns=columns,
                                       foreign_keys=foreign_keys,
                                       primary_keys=primary_keys,
                                       unique_keys=unique_keys,
                                       indexes=indexes,
                                       comment=t_comment)
                cache.tables.append(table_info)

        return cache
