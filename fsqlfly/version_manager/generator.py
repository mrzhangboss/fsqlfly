import attr
from copy import deepcopy
from typing import List
from fsqlfly.common import SchemaContent, VersionConfig, SchemaField, CanalMode, BlinkSQLType, FlinkConnectorType
from fsqlfly.db_helper import Connection, ResourceName, ResourceTemplate, SchemaEvent, ResourceVersion, Connector
from fsqlfly.utils.strings import dump_yaml, load_yaml, get_full_name


class IBaseResourceGenerator:
    def generate_schema_event(self, schema: SchemaContent, connection: Connection) -> SchemaEvent:
        raise NotImplementedError

    def generate_resource_name(self, connection: Connection, schema: SchemaEvent) -> ResourceName:
        raise NotImplementedError

    def generate_template(self, connection: Connection, schema: SchemaEvent,
                          resource_name: ResourceName) -> List[ResourceTemplate]:
        raise NotImplementedError

    def generate_default_version_config(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                                        template: ResourceTemplate) -> VersionConfig:
        raise NotImplementedError

    def generate_version(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                         template: ResourceTemplate) -> List[ResourceVersion]:
        raise NotImplementedError


class BaseResourceGenerator(IBaseResourceGenerator):
    def generate_schema_event(self, schema: SchemaContent, connection: Connection) -> SchemaEvent:
        return SchemaEvent(name=schema.name, info=schema.comment, database=schema.database,
                           connection_id=connection.id, comment=schema.comment, primary_key=schema.primary_key,
                           fields=dump_yaml([attr.asdict(x) for x in schema.fields]),
                           partitionable=schema.partitionable)

    def generate_resource_name(self, connection: Connection, schema: SchemaEvent) -> ResourceName:
        return ResourceName(name=schema.name, database=schema.database, connection_id=connection.id,
                            schema_version_id=schema.id, latest_schema_id=schema.id, is_latest=True,
                            full_name=get_full_name(connection.name, schema.database, schema.name))

    support_type = ['sink', 'source', 'both']

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
        return VersionConfig()

    def generate_version(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                         template: ResourceTemplate) -> List[ResourceVersion]:
        config = self.generate_default_version_config(connection, schema, name, template)

        config_str = dump_yaml(attr.asdict(config))
        return [ResourceVersion(name=ResourceVersion.latest_name(),
                                full_name=get_full_name(template.full_name, ResourceVersion.latest_name()),
                                is_system=True, is_latest=True,
                                connection_id=connection.id, resource_name_id=name.id, template_id=template.id,
                                schema_version_id=schema.id if schema else None, config=config_str)]


class SourceResourceGenerator(BaseResourceGenerator):
    support_type = ['source']


class SinkResourceGenerator(BaseResourceGenerator):
    support_type = ['sink']


class CanalResourceGenerator(BaseResourceGenerator):
    def __init__(self, connector: Connector):
        self._connector = connector
        self._mode = connector.connector_mode

    def _generate_update_fields(self, schema_event: SchemaEvent, config: VersionConfig) -> List[SchemaField]:
        cnt = self._connector
        fields = []
        config.exclude = '.*'
        schema_fields = [SchemaField(**x) for x in load_yaml(schema_event.fields)] if schema_event else []

        for schema in schema_fields:
            for suffix, tp in zip([cnt.before_column_suffix, cnt.after_column_suffix, cnt.update_suffix],
                                  [schema.type, schema.type, BlinkSQLType.BOOLEAN]):
                n_schema = deepcopy(schema)
                n_schema.type = tp
                n_schema.name = n_schema.name + suffix
                fields.append(n_schema)
        return fields

    def _generate_upsert_fields(self) -> List[SchemaField]:
        return [self._connector.binlog_type_name_field]

    def generate_version(self, connection: Connection, schema: SchemaEvent, name: ResourceName,
                         template: ResourceTemplate) -> List[ResourceVersion]:
        versions = []
        base = super(CanalResourceGenerator, self).generate_version(connection, schema, name, template)[0]
        for mode in self._mode:
            version = deepcopy(base)
            version.name = mode
            version.full_name = get_full_name(template.full_name, mode)

            fields = []
            config = super(CanalResourceGenerator, self).generate_default_version_config(connection, schema, name,
                                                                                         template)
            if mode == CanalMode.update:
                fields = self._generate_update_fields(schema, config)
            elif mode == CanalMode.upsert:
                fields = self._generate_upsert_fields()

            self._handle_time_field(fields)

            config.schema = [ResourceVersion.field2schema(x) for x in fields]
            version.config = dump_yaml(attr.asdict(config))
            versions.append(version)
        return versions

    def _handle_time_field(self, fields):
        if self._connector.rowtime_field:
            fields.append(self._connector.rowtime_field)
        if self._connector.process_time_field:
            fields.append(self._connector.process_time_field)
        if self._connector.db_execute_time_field:
            fields.append(self._connector.db_execute_time_field)


class SystemConnectorGenerator(BaseResourceGenerator):
    def __init__(self, connector: Connector):
        self.connector = connector
        typ = connector.target.type.code
        both, sink = BaseResourceGenerator.support_type, SinkResourceGenerator.support_type
        self.support_type = both if typ in FlinkConnectorType.both_resource() else sink

    def generate_resource_name(self, connection: Connection, schema: SchemaEvent) -> ResourceName:
        name = super(SystemConnectorGenerator, self).generate_resource_name(connection, schema)
        t_database, t_table = self.connector.get_transform_target_full_name(resource_name=name,
                                                                            connector=self.connector)

        name.database = t_database
        name.name = t_table
        name.full_name = get_full_name(connection.name, t_database, t_table)
        return name
