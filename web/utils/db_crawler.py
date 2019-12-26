# -*- coding:utf-8 -*-
import attr
import kafka
import warnings
import json
from typing import List, Union, Any, Optional, Set, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
from copy import deepcopy
from collections import defaultdict
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.engine import Engine
from sqlalchemy.engine.result import ResultProxy
from sqlalchemy.types import TypeDecorator, TypeEngine
from sqlalchemy import exc as sa_exc
from kafka.consumer.fetcher import ConsumerRecord
from kafka import TopicPartition


@attr.s
class ColumnInfo:
    name: str = attr.ib()
    type: TypeEngine = attr.ib()
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
class TopicField:
    name: str = attr.ib()
    typ: str = attr.ib()


@attr.s(auto_attribs=True)
class TopicInfo:
    name: str = attr.ib()
    is_json: bool = attr.ib(default=True)
    fields: List[TopicField] = attr.Factory(list)


@attr.s(auto_attribs=True)
class TableCache:
    typ: str = attr.ib()
    suffix: str = attr.ib()
    tables: List[TableInfo] = attr.Factory(list)
    databases: List[str] = attr.Factory(list)
    topics: List[TopicInfo] = attr.Factory(list)


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
            if typ == 'kafka':
                return self.get_kafka_cache(connection_url, suffix)
            raise NotImplementedError("Not Support Generate {} Cache".format(typ))

    def get_db_cache(self, connection_url: str, suffix: str, typ: str) -> TableCache:
        url = make_url(connection_url)

        engine = create_engine(url)
        databases = self.get_all_database(engine)
        cache = TableCache(suffix=suffix, typ=typ)
        insp = inspect(engine)
        cache.databases = databases
        for db in databases:

            table_names = set(insp.get_table_names(db))
            for n in table_names:
                t_comment = insp.get_table_comment(n, db)['text'] if typ != 'hive' else None
                columns = [ColumnInfo(**x) for x in insp.get_columns(n, db)]
                foreign_keys = [ForeignKey(**x) for x in insp.get_foreign_keys(n, db)] if typ != 'hive' else []
                unique_keys = [UniqueKey(**x) for x in insp.get_unique_constraints(n, db)] if typ != 'hive' else []
                indexes = [IndexKey(**x) for x in insp.get_indexes(n, db)]
                primary_keys = insp.get_primary_keys(n, db) if typ != 'hive' else []
                table_info = TableInfo(name=n, database=db, columns=columns,
                                       foreign_keys=foreign_keys,
                                       primary_keys=primary_keys,
                                       unique_keys=unique_keys,
                                       indexes=indexes,
                                       comment=t_comment)
                cache.tables.append(table_info)

        return cache

    @classmethod
    def get_kafka_topics(cls, connection_url: str) -> Set[str]:
        consumer = kafka.KafkaConsumer(bootstrap_servers=connection_url.split(','))
        res = consumer.topics()
        consumer.close()
        return res

    @classmethod
    def get_topic_offset(cls, topic: str, brokers: str) -> List[Tuple[int, int]]:
        from kafka import SimpleClient
        from kafka.protocol.offset import OffsetRequest, OffsetResetStrategy
        from kafka.common import OffsetRequestPayload

        client = SimpleClient(brokers)

        partitions = client.topic_partitions[topic]
        offset_requests = [OffsetRequestPayload(topic, p, -1, 10) for p in partitions.keys()]

        offsets_responses = client.send_offset_request(offset_requests)
        return [(r.partition, r.offsets[0]) for r in offsets_responses]

    @classmethod
    def get_topic_last_msg(cls, topic: str, offsets: List[Tuple[int, int]], brokers: str, nums: int = 10) -> List[
        Dict[TopicPartition, List[ConsumerRecord]]]:
        consumer = kafka.KafkaConsumer(bootstrap_servers=brokers.split(','))

        try:
            out = []
            for pt, offset in offsets:
                partition = kafka.TopicPartition(topic, pt)
                consumer.assign([partition])
                consumer.seek(partition, offset - nums if offset > nums else 0)
                msg = consumer.poll(timeout_ms=1000, max_records=nums, update_offsets=False)
                if msg:
                    out.append(msg)
            return out
        finally:
            consumer.close()

    def generate_topic_info(self, topic: str, brokers: str) -> TopicInfo:
        offsets = self.get_topic_offset(topic, brokers)
        data = self.get_topic_last_msg(topic, offsets, brokers)
        fields = defaultdict(Counter)
        for x in data:
            msgs = [msg.value.decode('utf-8', errors='ignore') for msg in x[list(x.keys())[0]]]
            for m in msgs:
                try:
                    data = json.loads(m)
                except json.JSONDecodeError as error:
                    return TopicInfo(name=topic, is_json=False)
                else:
                    if isinstance(data, dict):
                        for k, v in data.items():
                            typ = 'string'
                            if v is None:
                                typ = 'null'
                            elif isinstance(v, str):
                                typ = 'string'
                            elif isinstance(v, int) or isinstance(v, float):
                                typ = 'number'
                            elif isinstance(v, bool):
                                typ = 'boolean'
                            else:
                                warnings.warn('set type {} as string'.format(type(v)))

                            fields[k][typ] += 1
                    else:
                        return TopicInfo(name=topic, is_json=False)
        columns = []
        for key, field in fields.items():
            if len(field.keys()) == 1:
                column = TopicField(name=key, typ=list(field.keys())[0])
            else:
                data = sorted(field.keys(), key=lambda x: field[x], reverse=True)
                if field[data[0]] == 'null':
                    column = TopicField(name=key, typ=data[1])
                else:
                    column = TopicField(name=key, typ=data[0])
            columns.append(column)

        return TopicInfo(name=topic, fields=columns)

    def get_kafka_cache(self, connection_url: str, suffix: str) -> TableCache:
        with ThreadPoolExecutor() as executor:
            cache = TableCache(suffix=suffix, typ='kafka')
            topics = self.get_kafka_topics(connection_url)
            tasks = []
            for x in topics:
                tasks.append(executor.submit(self.generate_topic_info, x, connection_url))

            for future in as_completed(tasks):
                data = future.result()
                cache.topics.append(data)

            return cache
