# -*- coding:utf-8 -*-
from fsqlfly.common import *
import logzero
from copy import deepcopy
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql.sqltypes import TypeDecorator
from fsqlfly.db_helper import ResourceName, ResourceTemplate, ResourceVersion, Connection, SchemaEvent
from fsqlfly.utils.strings import load_yaml, dump_yaml, get_full_name
from fsqlfly.db_helper import DBSession, DBDao, Session, SUPPORT_MODELS, Connector, DBT


class UpdateStatus:
    def __init__(self, name: str = ''):
        self.schema_inserted = 0
        self.schema_updated = 0
        self.name_inserted = 0
        self.name_updated = 0
        self.template_inserted = 0
        self.template_updated = 0
        self.version_inserted = 0
        self.version_updated = 0
        self.name = name

    def update_schema(self, inserted: bool):
        self.schema_inserted += inserted
        self.schema_updated += not inserted

    def update_resource_name(self, inserted: bool):
        self.name_inserted += inserted
        self.name_updated += not inserted

    def update_template(self, inserted: bool):
        self.template_inserted += inserted
        self.template_updated += not inserted

    def update_version(self, inserted: bool):
        self.version_inserted += inserted
        self.version_updated += not inserted

    @property
    def info(self) -> str:
        header = f"{self.name}:\n\n\n" if self.name else ''
        return header + '\n'.join(['{}: {}'.format(x, getattr(self, x)) for x in dir(self) if x.endswith('ed')])


class BaseManager:
    use_comment = False
    use_primary = False
    renewable = True

    def __init__(self, connection_url: str, table_name_filter: NameFilter, db_type):
        self.connection_url = connection_url
        self.need_tables = table_name_filter
        self.db_type = db_type

    def run(self, target: DBT, session: Optional[Session] = None) -> DBRes:
        if not self.renewable:
            return DBRes.api_error("{} is Not renewable".format(target.name))
        status = UpdateStatus()

        session = DBSession.get_session() if session is None else session
        if isinstance(target, (Connection, ResourceName)):
            if isinstance(target, ResourceName):
                target = target.connection
            self.update_connection(status, session, target)
        elif isinstance(target, ResourceTemplate):
            if target.is_system:
                self.update_template(status, session, target.connection, target.schema_version, target.resource_name)
            else:
                self.update_version(status, session, target.connection, target.schema_version, target.resource_name,
                                    target)
        elif isinstance(target, ResourceVersion):
            if target.is_system:
                self.update_version(status, session, target.connection, target.schema_version, target.resource_name,
                                    target.template)
            else:
                self.update_version_cache(status, session, target)
        else:
            raise NotImplementedError("Not Support {}".format(type(target)))
        return DBRes(data=status.info)

    def update_connection(self, status: UpdateStatus, session: Session, connection: Connection):
        for content in self.update():
            schema = self.generate_schema_event(schema=content, connection=connection)
            schema, i = DBDao.upsert_schema_event(schema, session=session)
            status.update_schema(i)
            self.update_resource_name(status, session, connection, schema)

    def update_resource_name(self, status: UpdateStatus, session: Session, connection: Connection, schema: SchemaEvent):
        resource_name = self.generate_resource_name(connection, schema)
        resource_name, i = DBDao.upsert_resource_name(resource_name, session=session)
        status.update_resource_name(i)
        self.update_template(status, session, schema=schema, connection=connection, resource_name=resource_name)

    def update_template(self, status: UpdateStatus, session: Session, connection: Connection, schema: SchemaEvent,
                        resource_name: ResourceName):
        for template in self.generate_template(schema=schema, connection=connection, resource_name=resource_name):
            template, i = DBDao.upsert_resource_template(template, session=session)
            status.update_template(i)
            self.update_version(status, session, schema=schema, connection=connection, resource_name=resource_name,
                                template=template)

    def update_version(self, status: UpdateStatus, session: Session, connection: Connection, schema: SchemaEvent,
                       resource_name: ResourceName, template: ResourceTemplate):
        version = self.generate_default_version(connection, schema, resource_name, template)
        version, i = DBDao.upsert_resource_version(version, session=session)
        status.update_version(i)
        version.cache = dump_yaml(version.generate_version_cache())
        DBDao.save(version, session=session)

    def update_version_cache(self, status: UpdateStatus, session: Session, version: ResourceVersion):
        version.cache = dump_yaml(version.generate_version_cache())
        DBDao.save(version, session=session)
        status.update_version(False)

    @classmethod
    def generate_schema_event(cls, schema: SchemaContent, connection: Connection) -> SchemaEvent:
        return SchemaEvent(name=schema.name, info=schema.comment, database=schema.database,
                           connection_id=connection.id, comment=schema.comment, primary_key=schema.primary_key,
                           fields=dump_yaml([attr.asdict(x) for x in schema.fields]),
                           partitionable=schema.partitionable)

    def update(self) -> List[SchemaContent]:
        return list()

    @classmethod
    def generate_resource_name(cls, connection: Connection, schema: SchemaEvent) -> ResourceName:
        return ResourceName(name=schema.name, database=schema.database, connection_id=connection.id,
                            schema_version_id=schema.id, latest_schema_id=schema.id, is_latest=True,
                            full_name=get_full_name(connection.name, schema.database, schema.name))

    support_type = []

    def generate_template(self, connection: Connection, schema: SchemaEvent,
                          resource_name: ResourceName) -> List[ResourceTemplate]:
        res = []
        for x in self.support_type:
            temp = ResourceTemplate(name=x, type=x, is_system=True,
                                    full_name=get_full_name(resource_name.full_name, x),
                                    connection_id=connection.id, resource_name_id=resource_name.id,
                                    schema_version_id=schema.id)
            res.append(temp)
        return res

    def generate_default_version_config(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                                        template: ResourceTemplate) -> VersionConfig:
        raise NotImplementedError

    def generate_default_version(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                                 template: ResourceTemplate) -> ResourceVersion:
        config = self.generate_default_version_config(connection, schema, name, template)

        config_str = dump_yaml(attr.asdict(config))
        return ResourceVersion(name=ResourceVersion.latest_name(),
                               full_name=get_full_name(template.full_name, ResourceVersion.latest_name()),
                               is_system=True, is_latest=True,
                               connection_id=connection.id, resource_name_id=name.id, template_id=template.id,
                               schema_version_id=schema.id if schema else None, config=config_str)


class DatabaseManager(BaseManager):
    support_type = ['sink', 'source', 'both']

    def generate_default_version_config(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                                        template: ResourceTemplate) -> VersionConfig:
        config = VersionConfig()
        if template.type == 'sink':
            if name.get_config('insert_primary_key', typ=bool) and schema.primary_key:
                config.exclude = schema.primary_key
        return config

    use_comment = True
    use_primary = True

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
            name = types.INTEGER
            if typ.display_width == 1:
                name = types.BOOLEAN
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
        update_cache_name = '__update_cache_name'
        if hasattr(self, update_cache_name):
            return getattr(self, update_cache_name)
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
            comment = None
            if self.use_comment:
                try:
                    comment = insp.get_table_comment(table_name=tb, schema=db)['text']
                except NotImplementedError as err:
                    print('meet ', err)

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

            # print(schema)
            schemas.append(schema)
        setattr(self, update_cache_name, schemas)
        return schemas


class HiveManager(DatabaseManager):
    use_comment = False
    use_primary = False
    support_type = []

    hive_types = set(list(x for x in dir(BlinkHiveSQLType) if not x.startswith('__')))

    def _get_flink_type(self, typ: TypeDecorator) -> Optional[str]:
        from sqlalchemy.sql.sqltypes import (VARCHAR, String, CHAR, BINARY)

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


class ElasticSearchManager(DatabaseManager):
    def _es2flink(self, typ: str) -> Optional[str]:
        types = BlinkSQLType
        if typ in ("text", "keyword"):
            return types.STRING
        elif typ == 'long':
            return types.BIGINT
        elif typ == 'integer':
            return types.INTEGER
        elif typ == 'byte':
            return types.TINYINT
        elif typ == 'short':
            return types.SMALLINT
        elif typ == 'float':
            return types.FLOAT
        elif typ == 'binary':
            return types.BYTES
        elif typ == 'boolean':
            return types.BOOLEAN
        elif typ == 'date':
            return types.DATE

    def update(self):
        assert 'elasticsearch' == self.db_type
        from elasticsearch import Elasticsearch
        es = Elasticsearch(hosts=self.connection_url)
        schemas = []
        for index in es.indices.get_alias('*'):
            if index not in self.need_tables:
                continue

            schema = SchemaContent(name=index, type=self.db_type)
            mappings = es.indices.get_mapping(index)

            fields = []
            for k, v in mappings[index]['mappings']['properties'].items():
                field = SchemaField(name=k, type=self._es2flink(v['type']),
                                    nullable=True)
                if field.type is None:
                    logzero.logger.error(
                        "Not Add Column {} in {}.{} current not support : {}".format(field.name, schema.database,
                                                                                     schema.name, str(v['type'])))
                else:
                    fields.append(field)

            fields.sort(key=lambda x: x.name)

            schema.fields.extend(fields)

            print(schema)
            schemas.append(schema)

        return schemas


class HBaseManager(DatabaseManager):
    def update(self):
        assert 'hbase' == self.db_type
        import happybase
        host, port = self.connection_url.split(':')
        connection = happybase.Connection(host, int(port), autoconnect=True)
        schemas = []
        for x in connection.tables():
            tab = x.decode()
            table = connection.table(tab)
            schema = SchemaContent(name=tab, type=self.db_type)
            fields = []
            for fm in table.families():
                fields.append(SchemaField(name=fm.decode(), type=BlinkHiveSQLType.BYTES, nullable=True))
            schema.fields.extend(fields)
            schemas.append(schema)
        return schemas


class FileManger(BaseManager):
    renewable = False


class KafkaManger(BaseManager):
    renewable = False


SUPPORT_MANAGER = {
    'hive': HiveManager,
    'db': DatabaseManager,
    'kafka': KafkaManger,
    'hbase': HBaseManager,
    'elasticsearch': ElasticSearchManager,
    'file': FileManger
}


class ConnectorManager:
    def _run(self, connector: Connector, session: Session) -> DBRes:
        raise NotImplementedError

    def run(self, connector: Connector, _session: Optional[Session] = None) -> DBRes:
        session = DBSession.get_session() if _session is None else _session
        try:
            return self._run(connector, session)
        finally:
            session.close()


class CanalKafkaManager(DatabaseManager):
    support_type = ['source']

    renewable = True

    def __init__(self, connector: Connector, mode: str, cache: List[SchemaContent]):
        super().__init__(connector.target.url, NameFilter(), 'kafka')
        self._cache = cache
        self._connector = connector
        self._mode = mode

    def update(self) -> List[SchemaContent]:
        return self._cache

    def generate_default_version(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                                 template: ResourceTemplate) -> ResourceVersion:
        config = super(CanalKafkaManager, self).generate_default_version_config(connection, schema, name, template)
        version = super(CanalKafkaManager, self).generate_default_version(connection, schema, name, template)
        mode = self._mode
        version.name = mode
        version.full_name = get_full_name(template.full_name, mode)

        schema_fields = [SchemaField(**x) for x in load_yaml(schema.fields)] if schema else []
        row_field = self._connector.rowtime_field
        process_field = self._connector.process_time_field
        execute_time_field = self._connector.db_execute_time_field
        binlog_field = self._connector.binlog_type_name_field
        cnt = self._connector
        fields = []

        if mode == CanalMode.update:
            config.exclude = '.*'
            for schema in schema_fields:
                for suffix, tp in zip([cnt.before_column_suffix, cnt.after_column_suffix, cnt.update_suffix],
                                      [schema.type, schema.type, BlinkSQLType.BOOLEAN]):
                    n_schema = deepcopy(schema)
                    n_schema.type = tp
                    n_schema.name = n_schema.name + suffix
                    fields.append(n_schema)

        if row_field:
            fields.append(row_field)
        if process_field:
            fields.append(process_field)

        if self._mode == CanalMode.upsert:
            fields.append(binlog_field)

        if execute_time_field:
            fields.append(execute_time_field)

        config.schema = [ResourceVersion.field2schema(x) for x in fields]

        version.config = dump_yaml(attr.asdict(config))
        return version


class CanalManager:

    def __init__(self, connector: Connector, session: Session):
        db, kafka = connector.source, connector.target
        self.connector = connector
        self.db = db
        self.kafka = kafka
        self.session = session
        self.db_manager = DatabaseManager(db.url, NameFilter(db.include, db.exclude), db.type)
        self.mode = self.connector.connector_mode

    def run(self) -> DBRes:
        db, kafka, session, db_manager = self.db, self.kafka, self.session, self.db_manager
        res = []
        db_status = UpdateStatus('MySQL Status')
        db_manager.update_connection(db_status, session, db)
        res.append(db_status)
        for mode in self.mode:
            manager = CanalKafkaManager(self.connector, mode, db_manager.update())
            status = UpdateStatus('Canal {} Status'.format(mode))
            manager.update_connection(status, session, kafka)
            res.append(status)

        return DBRes(msg='\n\n'.join(x.info for x in res))


class CanalConnectorManager(ConnectorManager):
    def _run(self, connector: Connector, session: Session) -> DBRes:
        s_type, t_type = connector.source.type.code, connector.target.type.code
        assert s_type == 'db', 'Canal Source Type must be db current: {}'.format(s_type)
        assert t_type == 'kafka', 'Canal Target Type must be kafka current: {}'.format(t_type)

        manager = CanalManager(connector, session)

        return manager.run()


class SystemConnectorManager(ConnectorManager):
    pass


class BaseHelper:
    @classmethod
    def is_support(cls, mode: str) -> bool:
        return mode == 'update'

    @classmethod
    def update(cls, model: str, pk: int):
        raise NotImplementedError


class ConnectorHelper(BaseHelper):
    @classmethod
    def update(cls, model: str, pk: int):
        assert model == 'connector', 'Only support Connector Model'
        session = DBSession.get_session()
        obj = DBDao.one(base=SUPPORT_MODELS[model], pk=pk, session=session)
        manager = CanalConnectorManager() if obj.type.code == 'canal' else SystemConnectorManager()
        return manager.run(obj, session)


class ConnectionHelper(BaseHelper):
    @classmethod
    def update(cls, model: str, pk: int):
        session = DBSession.get_session()
        try:
            obj = DBDao.one(base=SUPPORT_MODELS[model], pk=pk, session=session)
            if isinstance(obj, Connection):
                name_filter = NameFilter(obj.include, obj.exclude)
                manager = SUPPORT_MANAGER[obj.type](obj.url, name_filter, obj.type)
            elif isinstance(obj, ResourceName):
                name_filter = NameFilter(obj.get_include())
                typ = obj.connection.type
                manager = SUPPORT_MANAGER[typ](obj.connection.url, name_filter, typ)
            else:
                name_filter = NameFilter()
                typ = obj.connection.type
                manager = SUPPORT_MANAGER[typ](
                    obj.connection.url,
                    name_filter,
                    typ
                )

            return manager.run(obj, session)
        finally:
            session.commit()
            session.close()


class ManagerHelper:
    @classmethod
    def get_helper(cls, model) -> Union[Type[ConnectorHelper], Type[ConnectionHelper]]:
        if model == 'connector':
            return ConnectorHelper
        else:
            return ConnectionHelper

    @classmethod
    def is_support(cls, model: str, mode: str) -> bool:
        return cls.get_helper(model).is_support(mode)

    @classmethod
    def update(cls, model: str, pk: Union[str, int]) -> DBRes:
        if model not in SUPPORT_MODELS:
            return DBRes.api_error(msg='{} not support'.format(model))
        return cls.get_helper(model).update(model, pk if isinstance(pk, int) else int(pk))
