from abc import ABC
from typing import Union, List
from sqlalchemy import create_engine
from fsqlfly.db_helper import Connector, ResourceName, ResourceVersion, Transform
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
    def build_sql(cls, target_database: str, target_table: str, version: ResourceVersion, connector: Connector) -> str:
        schemas = version.generate_version_cache()['schema']
        table = f"{connector.target.name}.{target_database}.{target_table}"
        source = version.db_full_name
        fields = ','.join("`{}`".format(x['name']) for x in schemas)
        key, value = connector.partition_key_value
        partition = f"PARTITION ( {key} = '{value}' ) " if connector.use_partition else ''
        way = 'OVERWRITE' if connector.system_overwrite else 'INTO'
        sql = f"INSERT {way} {table} {partition} select {fields} from {source};"

        return sql

    @classmethod
    def get_resource_name_default_version(cls, resource_name: ResourceName) -> ResourceVersion:
        require_version = None
        for version in resource_name.versions:
            if version.template.type == 'source':
                if version.is_default:
                    return version
                require_version = version
        msg = 'Not found require version Please check {}'.format(resource_name.full_name)
        assert require_version, msg
        return require_version

    def get_sink_default_version_name(self, resource_name: ResourceName) -> str:
        assert self.target.target.type.code == FlinkConnectorType.hive, "current only support target is hive"
        return self.target.target.name

    def get_flink_execution_type(self) -> str:
        if self.target.target.type.code == FlinkConnectorType.hive:
            return 'batch'
        return 'streaming'

    def _generate_transform(self, resource_names: List[ResourceName]) -> DBRes:
        updated = inserted = 0
        connector = self.target
        for resource_name in resource_names:
            name = connector.get_transform_name_format(resource_name=resource_name)
            require_version = self.get_resource_name_default_version(resource_name)
            sink_name = self.get_sink_default_version_name(resource_name)
            if sink_name is None:
                return DBRes.api_error(msg="Not found resource sink table {}".format(resource_name.full_name))
            require = require_version.full_name + ',' + sink_name
            t_database, t_table = connector.get_transform_target_full_name(resource_name=resource_name,
                                                                           connector=connector)
            execution = dict(planner='blink', type=self.get_flink_execution_type(),
                             parallelism=connector.system_execution_parallelism)
            execution['restart-strategy'] = connector.system_execution_restart_strategy
            transform = Transform(name=name, sql=self.build_sql(t_database, t_table, require_version, connector),
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

    # TODO: Long Parameter
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
        # TODO: Inappropriate Intimacy
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
            version = self.get_resource_name_default_version(resource_name)
            t_database, t_table = connector.get_transform_target_full_name(resource_name=resource_name,
                                                                           connector=connector)
            schemas = version.generate_version_cache()['schema']
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
