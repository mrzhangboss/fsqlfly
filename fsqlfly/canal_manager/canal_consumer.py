# -*- coding: utf-8 -*-
import time
import os
import logging
import sys
import json
from logzero import logger
from typing import Optional
from collections import defaultdict
from datetime import datetime
from random import randint
from argparse import ArgumentParser
import fsqlfly.settings

PRINT_EACH = 100
WAIT_TIMES = 0.5


class BaseCommand:
    def execute(self):
        parser = ArgumentParser()
        self.add_arguments(parser)
        print(sys.argv[2:])
        options = parser.parse_args(sys.argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        output = self.handle(*args, **cmd_options)
        return output

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        pass


class CanalConsumer(BaseCommand):
    help = 'Canal Consumer'
    bootstrap_servers = "localhost:9092"
    canal_execute_time_name = 'MYSQL_DB_EXECUTE_TIME'
    canal_event_type_name = 'MYSQL_DB_EVENT_TYPE'
    canal_before_column_suffix = '_before'
    canal_after_column_suffix = '_after'
    canal_update_suffix = '_updated'

    canal_table_filter = ".*\\..*"

    canal_host = 'localhost'
    canal_port = 11111
    canal_username = None
    canal_destination = None
    canal_password = None
    canal_client_id = None

    def add_arguments_for_canal_suffix(self, parser):
        parser.add_argument('--canal_execute_time_name', action='store', type=str, help='mysql execute time name',
                            default=None)
        parser.add_argument('--canal_event_type_name', action='store', type=str, help='mysql event type name',
                            default=None)
        parser.add_argument('--canal_before-column-suffix', action='store', type=str, help='kafka before column suffix',
                            default=None)
        parser.add_argument('--canal_after_column_suffix', action='store', type=str, help='kafka after column suffix',
                            default=None)
        parser.add_argument('--canal_update_suffix', action='store', type=str, help='kafka update column suffix',
                            default=None)

    def add_arguments(self, parser):
        parser.add_argument('--bootstrap_servers', action='store', help='kafka bootstrap servers split by ,',
                            default=None)
        parser.add_argument('--canal_host', action='store', help='canal server host you can set in .env file',
                            default=None)
        parser.add_argument('--canal_port', action='store', type=int, help='canal server port you can set in .env file',
                            default=None)
        parser.add_argument('--canal_destination', action='store', type=str,
                            help='canal server destination you can set in .env file',
                            default=None)

        parser.add_argument('--canal_username', action='store', type=str, help='canal instance username', default=None)
        parser.add_argument('--canal_password', action='store', type=str,
                            help='canal instance password you can set in .env file ', default=None)
        parser.add_argument('--canal_client_id', action='store', type=str,
                            help='canal instance client-id you can set in .env file ', default=str(randint(1, 1000)))
        parser.add_argument('--canal_table_filter', action='store', type=str,
                            help='canal instance table filter like ".*\\\\..*" you can set in .env file ', default=None)
        self.add_arguments_for_canal_suffix(parser)

    def init_global_params(self, options: dict):
        for k, v in options.items():
            if not hasattr(self, k) or k.startswith('_'):
                continue
            if v is None:
                # overwrite by default
                env_value = os.environ.get(k)
                if env_value is None:
                    default_value = getattr(self, k)
                    if default_value is None:
                        print('please set ', k, ' in your env or by command line')
                        exit(1)
                    setattr(self, k, default_value)
                else:
                    if k == 'canal_port':
                        env_value = int(env_value)
                    setattr(self, k, env_value)
            else:
                setattr(self, k, v)

    from canal.protocol.EntryProtocol_pb2 import RowData, EventType, Column

    SUPPORT_TYPE = {
        EventType.INSERT: "kafka_dc",
        EventType.DELETE: "kafka_dc",
        EventType.UPDATE: "kafka_u",
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
        if event_type == EventType.DELETE:
            data = self._generate_by_columns(row.beforeColumns)
            data[event_type_name] = event_type
        elif event_type == EventType.INSERT:
            data = self._generate_by_columns(row.afterColumns)
            data[event_type_name] = event_type
        elif event_type == EventType.UPDATE:
            update_suffix = self.canal_update_suffix
            data = {x.name + update_suffix: x.updated for x in row.afterColumns}
            before_data = self._generate_by_columns(row.beforeColumns, self.canal_before_column_suffix)
            after_data = self._generate_after_columns(row.afterColumns)
            data.update(before_data)
            data.update(after_data)
        else:
            raise Exception("Not support Now")
        assert execute_time not in data
        data[execute_time_name] = execute_time
        return json.dumps(data).encode('utf-8')

    def _generate_topic_name(self, database: str, table: str, event_type: int):
        typ = self.SUPPORT_TYPE[event_type]
        return f"{database}_{table}_{typ}"

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
                    topic_name = self._generate_topic_name(database, table, event_type)
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
                    logger.debug("{} wait for in {} already send {}".format(datetime.now(), sleep_times, send_times))
                sleep_times += 1

    def handle(self, *args, **options):
        self.init_global_params(options)
        from kafka import KafkaProducer

        from canal.client import Client
        try:
            producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers.split(','))

            client = Client()
            client.connect(host=self.canal_host, port=self.canal_port)
            client.check_valid(username=self.canal_username.encode(), password=self.canal_password.encode())
            client.subscribe(client_id=self.canal_client_id.encode(), destination=self.canal_destination.encode(),
                             filter=self.canal_table_filter.encode())
            self.run_forever(client, producer)
        finally:
            client.disconnect()
            producer.close()
