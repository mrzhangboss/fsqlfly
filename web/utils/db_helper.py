# -*- coding: utf-8 -*-
import attr
import warnings
from typing import List, Any, Optional, Dict, Set, Tuple, Union
from collections import namedtuple, defaultdict
from datetime import datetime, date
from heapq import nsmallest
from base64 import b64decode
from itertools import chain
from utils.db_crawler import TableCache, TableInfo, TopicInfo, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from utils.strings import build_select_sql, parse_sql


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


DBRelation = namedtuple('DBRelation', ['s_table', 's_fields', 't_table', 't_fields'])


@attr.s(auto_attribs=True)
class DBTableRelation:
    table: Union[TableInfo, TopicInfo] = attr.ib()
    typ: str = attr.ib()
    suffix: str = attr.ib()
    table_name: str = attr.ib()
    connection_url: str = attr.ib()
    relations: Dict[str, List[DBRelation]] = attr.Factory(dict)


@attr.s(auto_attribs=True)
class DBCache:
    tables: Dict[str, DBTableRelation] = attr.ib()


@attr.s(auto_attribs=True)
class DBResult:
    tableName: str = attr.ib()
    search: str = attr.ib()
    limit: int = attr.ib(default=-1)
    isEmpty: bool = attr.ib(default=False)
    data: List[Dict[str, Any]] = attr.Factory(list)
    fieldNames: List[str] = attr.Factory(list)
    lostTable: Optional[str] = attr.ib(default=None)


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

    def search(self, table: DBTableRelation, search: str, limit: int) -> DBResult:
        if table.typ != DBType.mysql:
            raise NotSupportException(f"{table.typ} not support in search")
        engine = self.get_db_engine(table)
        table_name = f'{table.table.database}.{table.table.name}'
        params = dict(parse_sql(search))
        offset = params.get('offset')
        full_sql = build_select_sql(search, table_name, limit=limit, offset=offset)

        with engine.connect() as con:
            data = con.execute(full_sql).fetchall()
            is_empty = len(data) == 0
            result = DBResult(tableName=DBProxy.get_global_table_name(table.table, table.suffix),
                              isEmpty=is_empty,
                              search=search,
                              limit=limit)
            for x in data:
                fields = x.keys()
                result.fieldNames = fields
                result.data.append(dict(zip(x.keys(), x.values())))

        return result


class DBProxy:
    source_cache_name = '__source'

    def __init__(self, caches: List[TableCache], assigned_relations: Optional[List[DBRelation]] = None, default_limit: int = 500):
        self._caches = caches
        self._connector = DBConnector(caches)
        self._assigned_relations = assigned_relations
        self._global_relations = self.build_global_relations()
        self._default_limit = default_limit

    def build_global_relations(self) -> Dict[Tuple[str, str], List[DBRelation]]:
        data = dict()

        graph = defaultdict(dict)

        for cache in self._caches:
            if cache.typ == DBType.mysql:
                for tb in cache.tables:
                    tb_name = self.get_global_table_name(tb, cache.suffix)
                    for foreign in tb.foreign_keys:
                        target_name = self.get_global_foreign_table_name(foreign, tb, cache.suffix)
                        graph[tb_name][target_name] = DBRelation(tb_name, foreign.constrained_columns, target_name,
                                                                 foreign.referred_columns)
                        graph[target_name][tb_name] = DBRelation(target_name,
                                                                 foreign.referred_columns, tb_name,
                                                                 foreign.constrained_columns)

        if self._assigned_relations:
            for x in self._assigned_relations:
                graph[x.s_table][x.t_table] = x
                graph[x.t_table][x.s_table] = DBRelation(x.t_table, x.t_fields, x.s_table, x.s_fields)

        all_routes = defaultdict(list)

        def run(start: str, target: str, head: str, father: list, route: set):
            cur_relation = graph[start][target]
            all_routes[(head, target)].append(father[::] + [cur_relation])
            route.add(target)
            if target in graph:
                for son in graph[target]:
                    if son in route:
                        continue
                    run(target, son, head, father[::] + [graph[start][target]], set(route))

        for key in graph:
            for x in graph[key]:
                if x != key:
                    run(key, x, key, [], {key})

        for k, v in all_routes.items():
            if len(v) > 1:
                first, second = nsmallest(2, v, key=lambda x: len(x))
                if len(first) == len(second):
                    warnings.warn("Same Route Length May be some wrong in relationship {}".format(k))
                data[k] = first
            else:
                data[k] = v[0]

        return data

    def generate_relations(self, table_name: str) -> Dict[str, List[DBRelation]]:
        data = dict()
        for key in self._global_relations:
            source, target = key
            if source == table_name:
                data[target] = self._global_relations[key]

        return data

    def generate_table_cache(self, table: Union[TableInfo, TopicInfo], typ: str, suffix: str) -> DBTableRelation:
        tb_name = self.get_global_table_name(table, suffix)
        relations = self.generate_relations(tb_name)
        return DBTableRelation(table=table, typ=typ, suffix=suffix, table_name=tb_name,
                               connection_url=table.connection_url,
                               relations=relations)

    @classmethod
    def get_global_table_name(cls, tb: Union[TableInfo, TopicInfo], suffix: str):
        if isinstance(tb, TopicInfo):
            return f"{suffix}.{tb.name}"
        else:
            return f"{tb.database}{suffix}.{tb.name}"

    @classmethod
    def get_global_foreign_table_name(cls, foreign_key: ForeignKey, table: Union[TopicInfo, TableInfo],
                                      suffix: str) -> str:
        if foreign_key.referred_schema:
            database = foreign_key.referred_schema
        else:
            database = table.database

        return f"{database}{suffix}.{foreign_key.referred_table}"

    def build_source_cache(self) -> DBCache:
        tables = dict()
        cache = DBCache(tables=tables)

        for ca in self._caches:
            if ca.typ != DBType.mysql:
                raise CacheGenerateNotSupportException("Not Support {} type Cache".format(ca.typ))
            for tb in chain(ca.tables, ca.topics):

                table_name = self.get_global_table_name(tb, ca.suffix)
                if table_name in tables:
                    raise CacheGenerateException(
                        f"At least Two Same database and table with same suffix, Error Table is {tb.database}.{tb.name} ")
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

    def build_search(self, father: DBResult, relation: DBRelation) -> str:
        assert len(relation.t_fields) == len(relation.s_fields)
        fields = [[] for _ in range(len(relation.t_fields))]
        for x in father.data:
            for i, f in enumerate(relation.s_fields):
                fields[i].append(x[f])

        names = []
        if len(father.data) == 1:
            for i, f in enumerate(relation.t_fields):
                value = fields[i][0]
                names.append(f'${f} = {value}')


        else:
            def convert_t(v: Any) -> str:
                if isinstance(v, str):
                    return f"'{v}'"
                elif isinstance(v, date):
                    return v.strftime('%Y-%m-%d')
                elif isinstance(v, datetime):
                    return v.strftime('%Y-%m-%d %H:%M:%S')
                return str(v)

            for i, f in enumerate(relation.t_fields):
                value = ' , '.join(map(convert_t, fields[i]))
                names.append(f'${f} in ({value})')
        return ' and '.join(names)

    def get_table(self, source_table: str, search: str, table_name: str, limit: int, *args, **kwargs) -> Optional[
        DBResult]:
        if source_table not in self.sources.tables:
            return None
        real_table = self.sources.tables[source_table]
        if table_name not in real_table.relations:
            return None

        source = self.get_search_table(search, self.sources.tables[source_table], limit=limit)
        if source_table == table_name:
            return source
        relations = real_table.relations[table_name]
        father = source
        target_search = search
        for x in relations:
            if father.isEmpty:
                return DBResult(table_name, isEmpty=True, search=target_search, lostTable=x.s_table)
            target_search = self.build_search(father, x)
            father = self.get_search_table(target_search, self.sources.tables[x.t_table], self._default_limit)

        return father
