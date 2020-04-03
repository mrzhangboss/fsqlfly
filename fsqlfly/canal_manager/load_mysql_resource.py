# -*- coding: utf-8 -*-
import warnings
from fsqlfly.models import Resource, Namespace
from copy import deepcopy
import yaml
from typing import List, Dict, Optional
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects.mysql.types import (_StringType, _FloatType, _IntegerType, DECIMAL, DATETIME, TIMESTAMP, BIT,
                                             TIME,
                                             BIGINT)

from sqlalchemy.sql.sqltypes import DATE, _Binary
from fsqlfly.canal_manager.canal_consumer import CanalConsumer


class Category:
    MYSQL = 'mysql'
    KAFKA = 'kafka'
    KAFKA_DELETE_AND_CREATE = 'kafka_dc'
    KAFKA_UPDATE = 'kafka_u'
    ES = 'es'


DEFAULT_FORMAT = {"property-version": 1, "type": "json", "derive-schema": True}


class LoadMySQLResource(CanalConsumer):
    help = 'Load Resource From MySQL'
    kafka_use_row_time = True
    kafka_row_time_name = 'mysql_row_time'
    kafka_process_time_name = 'flink_process_time'
    kafka_row_time_delay_second = 5
    kafka_connector_start_mode = "latest-offset"

    def add_arguments(self, parser):
        parser.add_argument('--host', action='store', help='mysql host')
        parser.add_argument('--database', action='store', help='mysql database')
        parser.add_argument('--category', action='store', help='from system', default="mysql",
                            choices=['mysql', 'es', 'kafka'])
        parser.add_argument('--tables', action='store', help='mysql tables', default="*")
        parser.add_argument('--kafka-bootstrap', action='store', help='kafka bootstrap servers',
                            default="localhost:9092", dest='kafka')
        parser.add_argument('--es-hosts', action='store', help='elastic search host port,sepe by ,',
                            default="http://localhost:9200", dest='es')
        parser.add_argument('--port', action='store', help='mysql port', default=3306, type=int)
        parser.add_argument('--password', action='store', help='mysql password, if not set must input when running',
                            default=None)
        parser.add_argument('--username', action='store', help='mysql username', default='root')
        parser.add_argument('--kafka_use_row_time', action='store_true', help='kafka use row time from mysql',
                            default=True)
        parser.add_argument('--kafka_row_time_delay_second', action='store', type=int,
                            help='kafka row time delay second',
                            default=None)

        parser.add_argument('--kafka_connector_start_mode', action='store', type=int,
                            help='kafka connector start mode support [earliest-offset|latest-offset|group-offsets|specific-offsets]',
                            default=None)
        parser.add_argument('--kafka_process_time_name', action='store', type=int,
                            help='kafka process time name',
                            default=None)
        self.add_arguments_for_canal_suffix(parser)

    def _init_global_args(self, options: dict):
        es_hosts = []
        for url in options['es'].split(','):
            protocol, h_p = url.split('//')
            host, port = h_p.split(':')
            es_hosts.append(dict(hostname=host, port=int(port), protocol=protocol))

        if len(es_hosts) < 1:
            warnings.warn("es host not good %s" % options['es-hosts'])

        self.ES_HOSTS = es_hosts
        self.JDBC_USER = options['username']
        self.JDBC_PASSWORD = options['password']

        host, port, database = options['host'], options['port'], options['database']
        self.JDBC_URL = f"jdbc:mysql://{host}:{port}/{database}?useSSL=false"
        self.NAMESPACE = database

        self.KAFKA_BOOTSTRAP_SERVERS = options['kafka']

    def _gen_kafka_connector(self, topic_name: str, typ: str, category: str) -> dict:
        return {
            "type": "kafka",
            "property-version": 1,
            "version": "universal",
            "topic": topic_name,
            "startup-mode": self.kafka_connector_start_mode,
            "properties": [
                {
                    "key": "bootstrap.servers",
                    "value": self.KAFKA_BOOTSTRAP_SERVERS,
                },
                {
                    "key": "group.id",
                    "value": f"{topic_name}_{typ}_{category}",
                }
            ]
        }

    def _gen_mysql_connector(self, table_name: str) -> dict:
        return {
            "type": "jdbc",
            "url": self.JDBC_URL,
            "table": table_name,
            "driver": "com.mysql.jdbc.Driver",
            "username": self.JDBC_USER,
            "password": self.JDBC_PASSWORD,

        }

    def _gen_es_connector(self, index: str) -> dict:
        return {
            "type": "elasticsearch",
            "version": "6",
            "hosts": self.ES_HOSTS,
            "index": index,
            "document-type": "data",
        }

    @classmethod
    def _gen_name(cls, name: str, typ: str, category: str) -> str:
        return name + '_' + category

    @property
    def canal_execute_time_name_field(self) -> dict:
        if self.kafka_use_row_time:
            row_time = {
                "timestamps": {
                    "type": "from-field",
                    "from": self.canal_execute_time_name
                },
                "watermarks": {
                    "type": "periodic-bounded",
                    "delay": self.kafka_row_time_delay_second * 1000
                }
            }
            return dict(name=self.kafka_row_time_name, type='TIMESTAMP', rowtime=row_time)
        return dict(name=self.canal_execute_time_name, type='BIGINT')

    @property
    def canal_event_type_name_field(self) -> dict:
        return dict(name=self.canal_event_type_name, type='INT')

    @property
    def kafka_process_time_name_field(self) -> dict:
        return dict(name=self.kafka_process_time_name, type='TIMESTAMP', proctime=True)

    @property
    def canal_kafka_added_schema(self):
        return self.canal_execute_time_name + " TIMESTAMP, " + self.canal_event_type_name + " INT"

    BOOLEAN_TYPE = "INT"

    def _generate_json_format(self, fields: list, category: str) -> dict:
        def _get_schema(fs: list) -> str:
            return 'ROW<{}>'.format(",".join(fs))

        data = {"property-version": 1, "type": "json"}

        if category == Category.KAFKA_DELETE_AND_CREATE:
            fs = ["{} {}".format(x['name'], x['type']) for x in fields] + [self.canal_kafka_added_schema]
            data["schema"] = _get_schema(fs)
        elif category == Category.KAFKA_UPDATE:
            fs = []
            fmt = "{name} {type}"
            for field in fields:
                k, v = field['name'], field['type']
                fs.append(fmt.format(name=k + self.canal_before_column_suffix, type=v))
                fs.append(fmt.format(name=k + self.canal_after_column_suffix, type=v))
                fs.append(fmt.format(name=k + self.canal_update_suffix, type=self.BOOLEAN_TYPE))
            fs.append(self.canal_kafka_added_schema)
            data['schema'] = _get_schema(fs)
        else:
            data["derive-schema"] = True

        return data

    def _gen_schema(self, fields: List[Dict[str, str]], category: str) -> list:
        if category == Category.KAFKA_DELETE_AND_CREATE:
            fields.append(self.canal_execute_time_name_field)
            fields.append(self.canal_event_type_name_field)
            fields.append(self.kafka_process_time_name_field)
            return fields
        elif category == Category.KAFKA_UPDATE:
            rlt = []
            for field in fields:
                k, v = field['name'], field['type']
                rlt.append(dict(name=k + self.canal_before_column_suffix, type=v))
                rlt.append(dict(name=k + self.canal_after_column_suffix, type=v))
                rlt.append(dict(name=k + self.canal_update_suffix, type=self.BOOLEAN_TYPE))
            rlt.append(self.canal_execute_time_name_field)
            rlt.append(self.kafka_process_time_name_field)
            return rlt
        else:
            return fields

    def _build_yml(self, name: str, typ: str, category: str, columns: List[dict]) -> str:
        data = dict()
        fields = []
        for col in columns:

            # print(col['type'], type(col['type']))
            _t = col['type']
            _n = col['name']
            _c = col['comment']
            t_name = None
            # print(str(_t))

            if isinstance(_t, _StringType) or isinstance(_t, _Binary):
                t_name = "STRING"
            elif isinstance(_t, BIT):
                t_name = "INT"
            elif isinstance(_t, _IntegerType):
                t_name = "INT"
                if isinstance(_t, BIGINT):
                    t_name = "BIGINT"
            elif isinstance(_t, _FloatType):
                t_name = "DOUBLE"
            elif isinstance(_t, DECIMAL):
                t_name = "DECIMAL"
            elif isinstance(_t, DATETIME):
                t_name = "TIMESTAMP"
            elif isinstance(_t, TIMESTAMP):
                t_name = "TIMESTAMP"
            elif isinstance(_t, DATE):
                t_name = "DATE"
            elif isinstance(_t, TIME):
                t_name = "TIME"

            assert t_name is not None
            # fields.append(dict(name=_n, type=t_name))
            fields.append(dict(name=_n, type=t_name))

        if category == Category.MYSQL:
            data['connector'] = self._gen_mysql_connector(name)
        elif category.startswith(Category.KAFKA):
            data['connector'] = self._gen_kafka_connector(f"{self.NAMESPACE}_{name}_{category}", typ, category)
            data['update-mode'] = 'append'
            data['format'] = self._generate_json_format(fields, category)
        elif category == Category.ES:
            data['connector'] = self._gen_es_connector(f"{self.NAMESPACE}_{name}")
            data['format'] = DEFAULT_FORMAT
            data['update-mode'] = 'append'
        else:
            raise Exception("Not Support category")
        data['schema'] = self._gen_schema(fields, category)
        data['type'] = typ

        rlt = yaml.dump(data)
        return rlt

    def create_resource_data(self, name: str, typ: str, category: str, columns: List[dict],
                             table_comment: Optional[str]) -> dict:
        print('create ', name, ' :', typ, '--', category, '@@', table_comment)
        obj = dict()
        obj['yaml'] = self._build_yml(name, typ, category, columns)
        obj['name'] = self._gen_name(name, typ, category)
        obj['info'] = table_comment
        obj['typ'] = typ
        return obj

    def create_resource(self, n: str, typ: str, category: str, resource: dict, columns: List[dict],
                        table_comment: Optional[str],
                        namespace_id: int):
        data = self.create_resource_data(n, typ, category, columns, table_comment)
        name = data['name']
        print('name is ', name, end='')
        data['namespace_id'] = namespace_id
        data['is_publish'] = True
        data['is_available'] = True
        if name not in resource:
            res = Resource.create(**data)
            print(' create a resource', res.id, res.name)
        else:
            resource = Resource.select().where(Resource.id == resource[name]).first()
            for k, v in data.items():
                setattr(resource, k, v)
            resource.save()
            print('update a resource ', resource.id, resource.name)

    def handle(self, *args, **options):
        if options['password'] is None:
            warnings.warn('you not set mysql password please input in command line!!!')
            password = input("Your MySQL Password:")
            options['password'] = password
        else:
            password = options['password']

        self._init_global_args(options)

        category = options['category']
        full_namespace = self.NAMESPACE + '_' + category

        namespace = Namespace.select().where(Namespace.name == full_namespace).first()

        if namespace is None:
            namespace = Namespace.create(name=full_namespace, info="auto generate by script")
        username, host, port, database = options['username'], options['host'], options['port'], options['database']
        db_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8"
        namespace_id = namespace.id

        engine = create_engine(db_url)
        insp = inspect(engine)
        tables_str = options['tables']
        table_names = set(insp.get_table_names())
        if tables_str == '*':
            need_tables = set(table_names)
        else:
            need_tables = set(tables_str.strip().split(','))

        resources = {x.name: x.id for x in Resource.select().where(Resource.namespace == namespace).objects()}
        for n in table_names:
            if n not in need_tables:
                continue
            t_comment = insp.get_table_comment(n)['text']
            cs = insp.get_columns(n)
            # self.create_resource(n, 'sink-table', category, resources, cs, t_comment, namespace_id)
            if category != Category.ES:
                if category == Category.KAFKA:
                    self.create_resource(n, 'source-table', Category.KAFKA_DELETE_AND_CREATE, resources, cs, t_comment,
                                         namespace_id)
                    self.create_resource(n, 'source-table', Category.KAFKA_UPDATE, resources, cs, t_comment,
                                         namespace_id)
                    self.create_resource(n, 'both', category, resources, cs, t_comment, namespace_id)
                else:
                    self.create_resource(n, 'both', category, resources, cs, t_comment, namespace_id)
            else:
                self.create_resource(n, 'sink-table', category, resources, cs, t_comment, namespace_id)

        table_nums = len(need_tables)
        print(f'Successfully load {table_nums} table from {database}: {tables_str}')
