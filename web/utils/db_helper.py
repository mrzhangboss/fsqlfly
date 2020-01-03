# -*- coding: utf-8 -*-
import attr
import warnings
import kafka
import json
from typing import List, Any, Optional, Dict, Tuple, Union, Iterable
from collections import namedtuple, defaultdict
from datetime import datetime, date
from heapq import nsmallest
from base64 import b64decode
from itertools import chain
from utils.db_crawler import TableCache, TableInfo, TopicInfo, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from utils.strings import build_select_sql, parse_sql, clean_sql
from utils.function_helper import build_function, Dict2Obj


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
    table_name: str = attr.ib()
    typ: str = attr.ib()
    search: str = attr.ib()
    limit: int = attr.ib(default=-1)
    isEmpty: bool = attr.ib(default=False)
    data: List[Dict[str, Any]] = attr.Factory(list)
    fieldNames: List[str] = attr.Factory(list)
    lostTable: Optional[str] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class WebResTableField:
    name: str = attr.ib()
    typ: str = attr.ib()
    unique: bool = attr.ib(default=False)
    primary: bool = attr.ib(default=False)


@attr.s(auto_attribs=True)
class WebResTable:
    tableName: str = attr.ib()
    typ: str = attr.ib()
    name: str = attr.ib()
    namespace: str = attr.ib()
    info: Optional[str] = attr.ib(default=None)
    fields: List[WebResTableField] = attr.Factory(list)


@attr.s(auto_attribs=True)
class WebResTables:
    data: List[WebResTable] = attr.Factory(list)


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

    def search_kafka(self, table: DBTableRelation, search: str, limit: int) -> DBResult:
        params = dict(parse_sql(search))
        auto_offset_reset = params.get('mode', 'latest')  # other earliest
        assert auto_offset_reset in ('latest', 'earliest')
        consumer = kafka.KafkaConsumer(table.table.name, bootstrap_servers=table.connection_url.split(','),
                                       auto_offset_reset=auto_offset_reset)
        msgs = consumer.poll(timeout_ms=1000, max_records=None if limit < 0 else limit, update_offsets=False)

        fields = params.get('fields', '*')
        field_names = [x.name for x in table.table.fields] if fields == '*' else fields.split(',')
        res = DBResult(table_name=DBProxy.get_global_kafka_table_name(table.table.name, table.suffix),
                       search=search, limit=limit,
                       fieldNames=field_names,
                       typ=table.typ)
        func = build_function(clean_sql(search))
        for k, v in msgs.items():
            for msg in v:
                data = json.loads(msg.value.decode('utf-8', errors='ignore'))

                cell = Dict2Obj(**data)
                if func(cell):
                    res.data.append(data)

        consumer.close()

        return res

    def search(self, table: DBTableRelation, search: str, limit: int) -> DBResult:
        """

        :param table:
        :param search: support offset, fields
        :param limit:
        :return:
        """
        if table.typ == DBType.kafka:
            return self.search_kafka(table, search, limit)
        engine = self.get_db_engine(table)
        table_name = f'{table.table.database}.{table.table.name}'
        params = dict(parse_sql(search))
        offset = params.get('offset')
        fields = params.get('fields', '*')
        full_sql = build_select_sql(search, table_name, limit=limit, offset=offset, fields=fields)

        def type_warp(vs: Iterable[Any]) -> Iterable[Any]:
            def _warp(v: Any) -> Any:
                if isinstance(v, bytes):
                    return v.decode('utf-8', errors='ignore')
                return v

            return (_warp(x) for x in vs)

        with engine.connect() as con:
            data = con.execute(full_sql).fetchall()
            is_empty = len(data) == 0
            result = DBResult(table_name=DBProxy.get_global_table_name(table.table, table.suffix),
                              isEmpty=is_empty,
                              search=search,
                              limit=limit,
                              typ=table.typ)
            field_names = None
            for x in data:
                if field_names is None:
                    field_names = list(x.keys())
                result.data.append(dict(zip(x.keys(), type_warp(list(x.values())))))

            if field_names is not None:
                result.fieldNames = field_names

        return result


class DBProxy:
    source_cache_name = '__source'

    def __init__(self, caches: List[TableCache], assigned_relations: Optional[List[DBRelation]] = None,
                 default_limit: int = 500):
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
    def get_global_kafka_table_name(cls, name: str, suffix: str):
        return f"{suffix}.{name}"

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
            for tb in chain(ca.tables, ca.topics):

                table_name = self.get_global_table_name(tb, ca.suffix)
                if table_name in tables:
                    raise CacheGenerateException(
                        f"At least Two Same database and table with same suffix, Error Table is {tb.database}.{tb.name} ")
                tables[table_name] = self.generate_table_cache(tb, ca.typ, ca.suffix)

        print(' update cache in ', datetime.now())

        setattr(self, self.source_cache_name, cache)
        return cache

    @property
    def sources(self) -> DBCache:
        if hasattr(self, self.source_cache_name):
            return getattr(self, self.source_cache_name)
        return self.build_source_cache()

    __table_meta_cache_name = '__TABLE_META_CACHE_NAME'

    def build_all_table_metas_cache(self) -> List[WebResTable]:
        data = list()

        for table_name, relation in self.sources.tables.items():
            table = relation.table
            fields = []
            if relation.typ == DBType.kafka:
                namespace = relation.suffix
                for x in table.fields:
                    fields.append(WebResTableField(name=x.name, typ=x.typ))
            else:
                namespace = table.database + relation.suffix
                primaries = set(table.primary_keys)

                unique = set()

                for x in table.unique_keys:
                    for k in x.column_names:
                        unique.add(k)

                for x in table.columns:
                    fields.append(
                        WebResTableField(name=x.name, typ=str(x.type), unique=x.name in unique,
                                         primary=x.name in primaries))

            data.append(WebResTable(tableName=table_name,
                                    name=table.name,
                                    namespace=namespace,
                                    fields=fields,
                                    info=table.comment if relation.typ != DBType.kafka else None,
                                    typ=relation.typ))

        setattr(self, self.__table_meta_cache_name, data)
        return data

    def rebuild_cache(self, caches: List[TableCache], assigned_relations: Optional[List[DBRelation]]):
        self._caches = caches
        self._assigned_relations = assigned_relations
        self.build_source_cache()
        self.build_all_table_metas_cache()

    @property
    def all_table_metas(self):
        if not hasattr(self, self.__table_meta_cache_name):
            return self.build_all_table_metas_cache()
        return getattr(self, self.__table_meta_cache_name)

    def api_get_all_table_metas(self):
        return WebResTables(data=self.all_table_metas)

    def api_get_related_table_metas(self, table_name: str) -> WebResTables:
        if table_name not in self.sources.tables:
            return WebResTables(data=[])
        tables = set(list(self.sources.tables[table_name].relations.keys()))
        return WebResTables(data=[x for x in self.all_table_metas if x.tableName in tables])

    def api_search_table(self, source_table: str, search: str, target_table: str, limit: int) -> DBResult:
        return self.get_table(source_table, search, target_table, limit)

    def get_search_table(self, search: str, table: DBTableRelation, limit: int):

        return self._connector.search(table, search, limit)

    @classmethod
    def get_symbal_define(cls, t_type: str) -> Tuple[str, str]:
        v_equal, v_null = '=', 'null'
        if t_type == DBType.kafka:
            v_equal, v_null = '==', 'None'
        return v_equal, v_null

    def build_search(self, father: DBResult, relation: DBRelation) -> str:
        assert len(relation.t_fields) == len(relation.s_fields)
        assert relation.t_table in self.sources.tables

        def convert_t(v: Any) -> str:
            if isinstance(v, str):
                return f"'{v}'"
            elif isinstance(v, datetime):
                return v.strftime("'%Y-%m-%d %H:%M:%S'")
            elif isinstance(v, date):
                return v.strftime("'%Y-%m-%d'")

            return str(v)

        fields = [[] for _ in range(len(relation.t_fields))]
        for x in father.data:
            for i, f in enumerate(relation.s_fields):
                fields[i].append(x.get(f))

        v_equal, v_null = self.get_symbal_define(self.sources.tables[relation.t_table].typ)

        def equal_line(k: str, v: Any) -> str:
            if v is None:
                return f"`{k}` is {v_null}"
            else:
                v = convert_t(v)
                return f"`{k}` {v_equal} {v}"

        def in_line(k: str, vs: List[Any]) -> str:
            contain_null = False
            unique = set()
            for x in vs:
                if x is None:
                    contain_null = True
                else:
                    unique.add(convert_t(x))
            out = []
            if unique:
                u_value = ' , '.join(unique)
                out.append("( `{k}` in ({value}) )".format(k=k, value=u_value))
            if contain_null:
                out.append(f" ( `{k}` is {v_null} )")

            return " or ".join(out)

        source_sum = len(father.data)
        field_sum = len(fields)
        assert field_sum > 0 and source_sum > 0
        if field_sum == 1:
            field_name = relation.t_fields[0]
            if source_sum == 1:
                k, v = field_name, fields[0][0]
                conditions = equal_line(k, v)
            else:
                k, vs = field_name, fields[0]
                conditions = in_line(k, vs)
        else:
            columns = set()
            for i in range(source_sum):
                line = []
                for j in range(field_sum):
                    field_name, field_value = relation.t_fields[j], fields[j][i]
                    line.append(equal_line(field_name, field_value))
                columns.add("( {} )".format(" and  ".join(line)))

            conditions = "( {} )".format("  or  ".join(columns))

        return conditions

    def get_table(self, source_table: str, search: str, target_table: str, limit: int, *args, **kwargs) -> Optional[
        DBResult]:
        if source_table not in self.sources.tables:
            return None
        real_table = self.sources.tables[source_table]
        if target_table != source_table and target_table not in real_table.relations:
            return None

        target_search = search
        target_limit = limit
        if target_table != source_table:
            relations = real_table.relations[target_table]
            assert len(relations) > 0
            target_search += ' /* fields = {} */ '.format(','.join(relations[0].s_fields))
            target_limit = -1

        source = self.get_search_table(target_search, real_table, limit=target_limit)
        if source_table == target_table:
            return source
        father = source
        # TODO: Faster speed by use mysql join instead of search by where
        for i, x in enumerate(relations):
            if father.isEmpty:
                return DBResult(target_table, isEmpty=True, search='', lostTable=x.s_table,
                                typ=self.sources.tables[target_table].typ)
            target_search = self.build_search(father, x)

            target_limit = self._default_limit
            if x.t_table != target_table:
                assert relations[i + 1].s_table == x.t_table
                target_search += ' /* fields = {} */ '.format(','.join(relations[i + 1].s_fields))
                target_limit = -1

            father = self.get_search_table(target_search, self.sources.tables[x.t_table], target_limit)

        return father
