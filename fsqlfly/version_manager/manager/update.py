from abc import ABC
from typing import Tuple
from fsqlfly.version_manager.dao import Dao
from fsqlfly.db_helper import (DBRes, ResourceName, ResourceVersion, ResourceTemplate, Connection, Connector, DBT,
                               SchemaEvent)
from fsqlfly.common import (NameFilter, FlinkConnectorType)
from fsqlfly.version_manager.base import BaseVersionManager
from fsqlfly.version_manager.generator import IBaseResourceGenerator
from fsqlfly.utils.strings import dump_yaml
from fsqlfly.version_manager.helpers.synchronization import SynchronizationHelper


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
        self.cache_updated = 0
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

    def update_cache(self):
        self.cache_updated += 1

    @property
    def info(self) -> str:
        header = f"{self.name}:\n\n\n" if self.name else ''
        return header + '\n'.join(['{}: {}'.format(x, getattr(self, x)) for x in dir(self) if x.endswith('ed')])


class UpdateManager(BaseVersionManager, ABC):
    def is_support(self) -> bool:
        return True


class ResourceVersionUpdateManager(UpdateManager):
    def _run(self):
        self.update_version(self.target)

    def run(self) -> DBRes:
        self._run()
        return DBRes(data=self.status.info)

    def update_version(self, version: ResourceVersion):
        version.cache = dump_yaml(version.generate_version_cache())
        self.dao.save(version)
        self.status.update_cache()

    @classmethod
    def get_source_sink(cls, target: DBT) -> Tuple[Connection, Connection]:
        if isinstance(target, (ResourceVersion, ResourceTemplate, ResourceName)):
            return target.connection, target.connection
        elif isinstance(target, Connection):
            return target, target
        elif isinstance(target, Connector):
            return target.source, target.target

    def __init__(self, target: DBT, dao: Dao, generator: IBaseResourceGenerator):
        self.target = target
        self.source, self.sink = self.get_source_sink(target)
        self.dao = dao
        self.status = UpdateStatus()
        self.gen = generator


class ResourceTemplateUpdateManager(ResourceVersionUpdateManager):
    def _run(self):
        assert isinstance(self.target, ResourceTemplate)
        obj = self.target
        self.update_template(obj.connection, obj.schema_version, obj.resource_name, obj)

    def update_template(self, connection: Connection, schema: SchemaEvent,
                        resource_name: ResourceName, template: ResourceTemplate):
        for version in self.gen.generate_version(connection, schema, resource_name, template):
            version, i = self.dao.upsert_resource_version(version)
            self.status.update_version(i)
            self.update_version(version)


class ResourceNameUpdateManager(ResourceTemplateUpdateManager):
    def _run(self):
        assert isinstance(self.target, ResourceName)
        obj = self.target
        self.update_connection(obj.connection, NameFilter(include=obj.db_name))

    def update_resource_name(self, connection: Connection, schema: SchemaEvent,
                             resource_name: ResourceName):
        for template in self.gen.generate_template(schema=schema, connection=connection, resource_name=resource_name):
            template, i = self.dao.upsert_resource_template(template)
            self.status.update_template(i)
            self.update_template(schema=schema, connection=connection, resource_name=resource_name, template=template)

    def update_connection(self, connection: Connection, name_filter: NameFilter):
        for content in SynchronizationHelper.synchronize(self.source, name_filter):
            schema = self.gen.generate_schema_event(schema=content, connection=connection)
            schema, i = self.dao.upsert_schema_event(schema)
            self.status.update_schema(i)
            resource_name = self.gen.generate_resource_name(connection, schema)
            resource_name, i = self.dao.upsert_resource_name(resource_name)
            self.status.update_resource_name(i)
            self.update_resource_name(connection, schema, resource_name)


class ConnectionUpdateManager(ResourceNameUpdateManager):
    def is_hive_sink(self):
        if isinstance(self.target, Connector):
            return self.target.target.type.code == FlinkConnectorType.hive
        return False

    def __init__(self, target: DBT, dao: Dao, generator: IBaseResourceGenerator, name_filter: NameFilter):
        super(ConnectionUpdateManager, self).__init__(target, dao, generator)
        self.name_filter = name_filter

    def _run(self):
        self.update_connection(self.sink, self.name_filter)
