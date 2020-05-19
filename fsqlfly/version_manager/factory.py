from typing import List
from fsqlfly.common import PageModelMode, PageModel, FlinkConnectorType, ConnectorType, NameFilter
from fsqlfly.db_helper import DBT, Connection, ResourceName, ResourceTemplate, ResourceVersion, Connector
from fsqlfly.version_manager.base import BaseVersionManager
from fsqlfly.version_manager.dao import Dao
from fsqlfly.version_manager.resource import (ResourceVersionUpdateManager, ResourceNameUpdateManager,
                                              ResourceTemplateUpdateManager, ConnectionUpdateManager)
from fsqlfly.version_manager.generator import (BaseResourceGenerator, SourceResourceGenerator, SinkResourceGenerator,
                                               CanalResourceGenerator)


class BaseManagerFactory:
    @classmethod
    def is_support(cls, model: str, obj: DBT) -> bool:
        raise NotImplementedError

    @classmethod
    def get_manager(cls, model: str, obj: DBT, dao: Dao) -> BaseVersionManager:
        if cls.is_support(model, obj):
            return cls.build(obj, dao)
        return BaseVersionManager.not_support_manager()

    @classmethod
    def build(cls, obj: DBT, dao: Dao) -> BaseVersionManager:
        raise NotImplementedError


class UpdateManagerFactory(BaseManagerFactory):
    @classmethod
    def get_connection(cls, obj: DBT):
        if isinstance(obj, (ResourceVersion, ResourceTemplate, ResourceName)):
            return obj.connection
        if isinstance(obj, Connection):
            return obj
        elif isinstance(obj, Connector):
            return obj.source
        else:
            raise NotImplementedError("Can't get connection from {}".format(obj.as_dict()))

    @classmethod
    def is_canal(cls, obj: DBT):
        return isinstance(obj, Connector) and obj.type.code == ConnectorType.canal

    @classmethod
    def is_system_connector(cls, obj: DBT):
        return isinstance(obj, Connector) and obj.type.code == ConnectorType.system

    @classmethod
    def get_generator(cls, obj: DBT) -> BaseResourceGenerator:
        if cls.is_canal(obj):
            return CanalResourceGenerator(obj)
        if cls.is_system_connector(obj):
            return SinkResourceGenerator()
        con = cls.get_connection(obj)
        c_type = con.type.code
        if c_type in FlinkConnectorType.both_resource():
            generator = BaseResourceGenerator()
        elif c_type == FlinkConnectorType.elasticsearch:
            generator = SinkResourceGenerator()
        else:
            raise NotImplementedError("Not Support {} schema parser".format(c_type))
        return generator

    @classmethod
    def build(cls, obj: DBT, dao: Dao) -> BaseVersionManager:
        generator = cls.get_generator(obj)
        if isinstance(obj, ResourceVersion):
            return ResourceVersionUpdateManager(obj, dao, generator)
        elif isinstance(obj, ResourceName):
            return ResourceNameUpdateManager(obj, dao, generator)
        elif isinstance(obj, ResourceTemplate):
            return ResourceTemplateUpdateManager(obj, dao, generator)
        elif isinstance(obj, Connection):
            return ConnectionUpdateManager(obj, dao, generator, NameFilter(obj.include, obj.exclude))
        elif isinstance(obj, Connector):
            return ConnectionUpdateManager(obj, dao, generator, obj.table_filter)

        raise NotImplementedError("Not Support {} in UpdateManagerFactory".format(obj.as_dict()))

    @classmethod
    def is_support(cls, model: str, obj: DBT) -> bool:
        return model in PageModel.renewable()


class ManagerFactory:
    @classmethod
    def get_manager(cls, model: str, mode: str, obj: DBT, dao: Dao) -> BaseVersionManager:
        if mode == PageModelMode.update:
            return UpdateManagerFactory.get_manager(model, obj, dao)
        raise NotImplementedError("current not support {} - {} ".format(model, mode))


class ResourceGeneratorFactor:
    pass
