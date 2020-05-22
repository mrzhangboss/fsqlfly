from abc import ABC
from typing import List, Optional
from sqlalchemy import create_engine
from fsqlfly.db_helper import Connector, ResourceName, ResourceVersion, Transform, Connection
from fsqlfly.common import DBRes, ConnectorType, BlinkSQLType, BlinkHiveSQLType, FlinkConnectorType
from fsqlfly.version_manager.base import BaseVersionManager
from fsqlfly.version_manager.dao import Dao
from fsqlfly.utils.strings import dump_yaml


class InitManager(BaseVersionManager, ABC):
    def __init__(self, target: Connector, dao: Dao):
        self.target = target
        self.dao = dao

    def is_support(self) -> bool:
        return self.target.type.code == ConnectorType.system


class ConnectorInitTransformManager(InitManager):
    def run(self) -> DBRes:
        return self.generate_transform()

    @classmethod
    def _(cls, tb: str) -> str:
        return f'`{tb}`'

    def get_sql_table_name(self, version: ResourceVersion):
        if version.connection.type.code == FlinkConnectorType.hive:
            return version.resource_name.full_name
        return self._(version.db_full_name)

    def build_sql(self, target: ResourceVersion, source: ResourceVersion, connector: Connector) -> str:
        schemas = target.generate_version_schema()
        table = self.get_sql_table_name(target)
        source = self.get_sql_table_name(source)
        fields = ','.join("`{}`".format(x['name']) for x in schemas)
        key, value = connector.partition_key_value
        partition = f"PARTITION ( {key} = '{value}' ) " if connector.use_partition else ''
        way = 'OVERWRITE' if connector.system_overwrite else 'INTO'
        sql = f"INSERT {way} {table} {partition} select {fields} from {source};"

        return sql

    @classmethod
    def is_hive_source(cls, connection: Connection) -> bool:
        return connection.type.code == FlinkConnectorType.hive

    def get_source_name(self, version: ResourceVersion) -> str:
        if self.is_hive_source(version.connection):
            return version.connection.name
        return version.full_name

    def get_source_default_version(self, resource_name: ResourceName) -> ResourceVersion:
        return self.dao.get_default_source_version(resource_name.database, resource_name.name,
                                                   resource_name.connection.id)

    def get_sink_default_version(self, t_database: str, t_table: str) -> Optional[ResourceVersion]:
        return self.dao.get_default_sink_version(t_database, t_table, self.target.target.id)

    def get_flink_execution_type(self) -> str:
        if self.target.target.type.code == FlinkConnectorType.hive:
            return 'batch'
        return 'streaming'

    def _generate_transform(self, resource_names: List[ResourceName]) -> DBRes:
        updated = inserted = 0
        connector = self.target
        for resource_name in resource_names:
            t_database, t_table = connector.get_transform_target_full_name(resource_name=resource_name,
                                                                           connector=connector)
            name = connector.get_transform_name_format(resource_name=resource_name)
            source_version = self.get_source_default_version(resource_name)
            if source_version is None:
                return DBRes.api_error(msg="Not found resource source table {}".format(resource_name.full_name))
            sink_version = self.get_sink_default_version(t_database, t_table)
            if sink_version is None:
                return DBRes.api_error(msg="Not found resource sink table {}".format(resource_name.full_name))
            require = self.get_source_name(source_version) + ',' + self.get_source_name(sink_version)

            execution = dict(planner='blink', type=self.get_flink_execution_type(),
                             parallelism=connector.system_execution_parallelism)
            execution['restart-strategy'] = connector.system_execution_restart_strategy
            transform = Transform(name=name, sql=self.build_sql(sink_version, source_version, connector),
                                  require=require, connector_id=connector.id, yaml=dump_yaml(dict(execution=execution)))
            transform, i = self.dao.upsert_transform(transform)
            inserted += i
            updated += not i

        msg = 'update: {}\ninserted: {}'.format(updated, inserted)
        return DBRes(msg=msg)

    def _run(self, resource_names: List[ResourceName]):
        return self._generate_transform(resource_names)

    def generate_transform(self) -> DBRes:
        connector = self.target
        need_tables = connector.need_tables
        source, target = connector.source, connector.target
        if not connector.source.resource_names:
            return DBRes.api_error("Not Found Any Resource Name in Connection {}".format(source.name))
        resource_names = [x for x in connector.source.resource_names if x.db_name in need_tables]
        return self._run(resource_names)


class HiveInitTransformManager(ConnectorInitTransformManager):
    @classmethod
    def flink2hive(cls, typ: str) -> str:
        if typ == BlinkSQLType.TIMESTAMP:
            return 'TIMESTAMP'
        if typ == BlinkSQLType.BYTES:
            return BlinkHiveSQLType.BINARY
        return typ

    def build_hive_create_sql(self, target_database: str, target_table: str, schema: list) -> List[str]:
        res = []
        connector = self.target
        drop_table = f'DROP TABLE IF EXISTS `{target_database}`.`{target_table}`'
        create_header = f'CREATE TABLE `{target_database}`.`{target_table}` ('
        cols = []
        for x in schema:
            typ = self.flink2hive(x['data-type'])
            col = '`{}` {}'.format(x['name'], typ)
            cols.append(col)
        res.extend([create_header])
        res.append(','.join(cols))
        res.append(')')
        if connector.use_partition:
            key, _ = connector.partition_key_value
            partition = f"PARTITIONED BY ({key} STRING)"
            res.append(partition)

        if connector.get_config('hive_row_format'):
            res.append(connector.get_config('hive_row_format'))
        return [drop_table, '\n'.join(res)]

    def create_hive_table(self, resource_names: List[ResourceName]) -> DBRes:
        connector = self.target
        engine = create_engine(connector.target.url)
        for resource_name in resource_names:
            t_database, t_table = connector.get_transform_target_full_name(resource_name=resource_name,
                                                                           connector=connector)
            version = self.get_sink_default_version(t_database, t_table)
            schemas = version.generate_version_schema()
            for sql in self.build_hive_create_sql(t_database, t_table, schemas):
                print(sql)
                engine.execute(sql)

        return DBRes()

    def _run(self, resource_names: List[ResourceName]):
        self.create_hive_table(resource_names)
        return self._generate_transform(resource_names)


class ListInitJobManager(ConnectorInitTransformManager):
    def _run(self, resource_names: List[ResourceName]):
        res = []
        for resource_name in resource_names:
            name = self.target.get_transform_name_format(resource_name=resource_name)
            res.append(name)
        return DBRes(data=res)
