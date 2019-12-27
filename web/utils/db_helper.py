# -*- coding: utf-8 -*-
import attr
from typing import List, Any, Optional, Dict
from base64 import b64decode
from utils.db_crawler import TableCache, TableInfo
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class CacheGenerateException(Exception):
    pass


class NotSupportException(Exception):
    pass


class CacheGenerateNotSupportException(NotSupportException):
    pass


class DBType:
    mysql = 'mysql'
    kafka = 'kafka'
    hive = 'hive'


@attr.s(auto_attribs=True)
class DBTableRelation:
    table: TableInfo = attr.ib()
    typ: str = attr.ib()
    suffix: str = attr.ib()
    table_name: str = attr.ib()
    connection_url: str = attr.ib()


@attr.s(auto_attribs=True)
class DBCache:
    tables: Dict[str, DBTableRelation] = attr.ib()


class DBConnector:
    def __init__(self, caches: List[TableCache]):
        self._caches = caches
        self._engines = dict()

    def get_db_engine(self, table: DBTableRelation) -> Engine:
        if table.connection_url in self._engines:
            return self._engines[table.connection_url]
        connection_url = b64decode(table.connection_url).decode()
        self._engines[table.connection_url] = create_engine(connection_url)
        return self._engines[table.connection_url]

    def search(self, table: DBTableRelation, search: str, limit: int) -> List[Any]:
        if table.typ != DBType.mysql:
            raise NotSupportException(f"{table.typ} not support in search")
        engine = self.get_db_engine(table)
        table_name = f'{table.table.database}.{table.table.name}'
        where_condition = search.replace('$', f'{table_name}.')

        with engine.connect() as con:
            return con.execute(f'select * from {table_name} where {where_condition} limit {limit}').fetchall()


class DBProxy:
    source_cache_name = '__source'

    def __init__(self, caches: List[TableCache]):
        self._caches = caches
        self._connector = DBConnector(caches)

    def generate_connection(self, caches: List[TableInfo]):
        pass

    def generate_table_cache(self, table: TableInfo, typ: str, suffix: str) -> DBTableRelation:
        caches = self._caches
        tb_name = f"{table.database}{suffix}.{table.name}"
        return DBTableRelation(table=table, typ=typ, suffix=suffix, table_name=tb_name,
                               connection_url=table.connection_url)

    def build_source_cache(self) -> DBCache:
        tables = dict()
        cache = DBCache(tables=tables)

        for ca in self._caches:
            if ca.typ != DBType.mysql:
                raise CacheGenerateNotSupportException("Not Support {} type Cache".format(ca.typ))
            for tb in ca.tables:

                table_name = f"{tb.database}{ca.suffix}.{tb.name}"
                if table_name in tables:
                    raise CacheGenerateException(
                        f"At least Two Same databae and table with same suffix, Error Table is {tb.database}.{tb.name} ")
                tables[table_name] = self.generate_table_cache(tb, ca.typ, ca.suffix)

        setattr(self, self.source_cache_name, cache)
        return cache

    @property
    def sources(self) -> DBCache:
        if hasattr(self, self.source_cache_name):
            return getattr(self, self.source_cache_name)
        return self.build_source_cache()

    def get_search_table(self, search: str, table: DBTableRelation, limit: int):

        return self._connector.search(table, search, limit)

    def get_table(self, source_table: str, search: str, table_name: str, limit: int, *args, **kwargs) -> List[Any]:
        if source_table not in self.sources.tables:
            return []

        return self.get_search_table(search, self.sources.tables[source_table], limit=limit)
