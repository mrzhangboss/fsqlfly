from fsqlfly.common import *
import time
import os
import logging
import sys
import json
from logzero import logger
from typing import Optional, Dict, Tuple
from collections import defaultdict
from datetime import datetime
from random import randint
from configparser import ConfigParser, SectionProxy
from argparse import ArgumentParser
from fsqlfly.db_helper import DBSession, Connector, Connection, Session, ResourceVersion

PRINT_EACH = 100
WAIT_TIMES = 0.5


class Consumer:
    def __init__(self, canal_mode: CanalMode, bootstrap_servers: str, topics: Dict[Tuple[str, str, str], str], *args,
                 table_filter: Optional[str], canal_host: str, canal_port: str, canal_username: str,
                 canal_password: str, canal_destination: str, canal_client_id: str,
                 binlog_type_name: str, rowtime_from: str, before_column_suffix: str, after_column_suffix: str,
                 update_suffix: str, **kwargs):
        self._mode = canal_mode
        self.bootstrap_servers = bootstrap_servers
        self.topics = topics
        self.canal_execute_time_name = rowtime_from
        self.canal_event_type_name = binlog_type_name
        self.canal_before_column_suffix = before_column_suffix
        self.canal_after_column_suffix = after_column_suffix
        self.canal_update_suffix = update_suffix

        self.canal_table_filter = table_filter if table_filter else ".*\\..*"

        self.canal_host = canal_host
        self.canal_port = int(canal_port)
        self.canal_username = canal_username
        self.canal_destination = canal_destination
        self.canal_password = canal_password
        self.canal_client_id = canal_client_id

    @classmethod
    def build_topics(cls, connection: Connection, session: Session) -> Dict[Tuple[str, str, str], str]:
        topics = dict()
        for version in session.query(ResourceVersion).filter(ResourceVersion.connection_id == connection.id).all():
            if version.name in CANAL_MODE:
                name = version.resource_name
                conn = version.get_connection_connector()
                assert isinstance(conn, dict)
                w_str = f'please check connection {connection.name} config not found topic'
                assert isinstance(conn, dict) and conn.get('topic') is not None, w_str
                topics[name.database, name.name, version.name] = conn['topic']
        return topics

    @classmethod
    def build(cls, pk: Union[str, int]) -> 'Consumer':
        session = DBSession.get_session()
        try:
            query = session.query(Connector)
            if isinstance(pk, int) or pk.isdigit():
                query = query.filter(Connector.id == pk)
            else:
                query = query.filter(Connector.name == pk)

            connector = query.first()
            assert connector, f"Not Found Connector {pk}"
            c_type = connector.type.code
            assert c_type == 'canal', f'connector  {pk} type must be canal current: {c_type}'
            assert connector.target.type.code == 'kafka'
            kafka = connector.target

            topics = cls.build_topics(kafka, session)
            return Consumer(connector.connector_mode, kafka.url, topics, **connector.get_config_parser()['canal'])
        finally:
            session.close()

    from canal.protocol.EntryProtocol_pb2 import RowData, EventType, Column

    SUPPORT_TYPE = {
        EventType.INSERT: CanalMode.insert,
        EventType.DELETE: CanalMode.delete,
        EventType.UPDATE: CanalMode.update,
    }

    @classmethod
    def _convert_type(cls, v: Column) -> any:
        val = v.value
        typ = v.sqlType
        if val is None or len(val) == 0:
            return None
        # type id from java.sql.Types.java
        if typ in {-7, -6, 5, 4, -5, 16}:  # int bool 16 also parse int
            return int(val)
        elif typ in {6, 7, 8, 2, 3}:  # float
            return float(val)
        elif typ == 91:  # DATE 91
            return val
        elif typ == 92 and val is not None:  # TIME 92
            return val + "Z"
        elif typ == 93 and val is not None:  # TIMESTAMP 93
            return val.replace(' ', 'T') + 'Z'
        return val

    def _generate_by_columns(self, columns: list, name_suffix: Optional[str] = None) -> dict:
        return {(x.name if name_suffix is None else x.name + name_suffix): self._convert_type(x) for x in columns}

    def _convert_after_column(self, value: any, updated: bool) -> any:
        if updated:
            return self._convert_type(value)
        return None

    def _generate_after_columns(self, columns: list):
        return {(x.name + self.canal_after_column_suffix): self._convert_after_column(x, x.updated) for x in
                columns if x.updated}

    def _generate_notice(self, event_type: int, row: RowData, execute_time: str) -> bytes:
        from canal.protocol.EntryProtocol_pb2 import EventType
        _cv = self._convert_type
        execute_time_name = self.canal_execute_time_name
        event_type_name = self.canal_event_type_name
        if self._mode.is_upsert():
            data = self._generate_by_columns(row.beforeColumns)
            after_data = self._generate_by_columns(row.afterColumns)
            data.update(after_data)
            data[event_type_name] = event_type
            assert event_type in (EventType.DELETE, EventType.INSERT, EventType.UPDATE)
        elif event_type == EventType.DELETE:
            data = self._generate_by_columns(row.beforeColumns)
        elif event_type == EventType.INSERT:
            data = self._generate_by_columns(row.afterColumns)
        elif event_type == EventType.UPDATE:
            update_suffix = self.canal_update_suffix
            data = {x.name + update_suffix: x.updated for x in row.afterColumns}
            data = self._generate_by_columns(row.beforeColumns, self.canal_before_column_suffix)
            after_data = self._generate_after_columns(row.afterColumns)
            data.update(data)
            data.update(after_data)
        else:
            raise Exception("Not support Now")
        assert execute_time not in data
        data[execute_time_name] = execute_time
        return json.dumps(data, ensure_ascii=False).encode('utf-8')

    def _generate_topic_name(self, database: str, table: str, event_type: str) -> Optional[str]:
        name = database, table, event_type
        if name in self.topics:
            return self.topics[name]

    @classmethod
    def _convert_utc_time(cls, timestamp: int) -> str:
        date = datetime.fromtimestamp(timestamp / 1000)
        # three way for parse timestamp
        # s = date.strftime("%FT%H:%M:%S.%f")[:-3] + "Z"
        # s = date.isoformat('T', timespec='milliseconds') + 'Z'
        s = date.strftime("%FT%H:%M:%S.%f") + "Z"
        return s

    def run_forever(self, client, producer):
        from canal.protocol import EntryProtocol_pb2
        from canal.protocol.EntryProtocol_pb2 import EntryType
        print(datetime.now(), " start running")
        topics = defaultdict(int)
        sleep_times, send_times = 0, 0
        last_execute_time, add_million_seconds = -1, 0
        while True:
            message = client.get(100)
            entries = message['entries']
            for entry in entries:
                entry_type = entry.entryType
                if entry_type in (EntryType.TRANSACTIONBEGIN, EntryType.TRANSACTIONEND):
                    continue
                row_change = EntryProtocol_pb2.RowChange()
                row_change.MergeFromString(entry.storeValue)
                header = entry.header
                database = header.schemaName
                table = header.tableName
                event_type = header.eventType

                # try add million second when meet same execute time
                fix_execute_time = header.executeTime
                if last_execute_time == header.executeTime:
                    if add_million_seconds < 999:
                        add_million_seconds += 1
                        fix_execute_time = header.executeTime + add_million_seconds
                    else:
                        print('over 1000 event in one seconds')
                        fix_execute_time = header.executeTime + add_million_seconds
                else:
                    last_execute_time = header.executeTime
                    add_million_seconds = 0

                row_time = self._convert_utc_time(fix_execute_time)

                logging.debug(' '.join(str(x) for x in
                                       [row_time, fix_execute_time, header.executeTime, header.logfileOffset,
                                        add_million_seconds]))
                for row in row_change.rowDatas:
                    msg = self._generate_notice(event_type, row, row_time)
                    event_type_name = self.SUPPORT_TYPE[event_type]
                    topic_name = self._generate_topic_name(database, table, event_type_name)
                    if topic_name is None or not self._mode.is_support(event_type_name):
                        print('filter {} {} {} - topic{}'.format(database, table, event_type_name, topic_name))
                        continue

                    if topic_name not in topics:
                        print(topic_name, 'get')
                    topics[topic_name] += 1
                    producer.send(topic_name, value=msg)
                    send_times += 1
            if not entries:
                time.sleep(WAIT_TIMES)
                if sleep_times % PRINT_EACH == 0:
                    for t, n in topics.items():
                        print(' Topic: ', t, ' send ', n)
                    topics = defaultdict(int)
                    logger.debug(
                        "{} wait for in {} already send {}".format(datetime.now(), sleep_times, send_times))
                sleep_times += 1

    def run(self):
        from kafka import KafkaProducer
        from canal.client import Client
        client = Client()
        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers.split(','))

        try:

            client.connect(host=self.canal_host, port=self.canal_port)
            client.check_valid(username=self.canal_username.encode(), password=self.canal_password.encode())
            client.subscribe(client_id=self.canal_client_id.encode(), destination=self.canal_destination.encode(),
                             filter=self.canal_table_filter.encode())
            self.run_forever(client, producer)
        finally:
            client.disconnect()
            producer.close()
