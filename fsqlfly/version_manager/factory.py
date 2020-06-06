from typing import Type
from fsqlfly.common import PageModelMode, PageModel, FlinkConnectorType, ConnectorType, NameFilter
from fsqlfly.db_helper import DBT, Connection, ResourceName, ResourceTemplate, ResourceVersion, Connector
from fsqlfly.version_manager.base import BaseVersionManager
from fsqlfly.version_manager.dao import Dao
from fsqlfly.version_manager.manager.update import (ResourceVersionUpdateManager, ResourceNameUpdateManager,
                                                    ResourceTemplateUpdateManager, ConnectionUpdateManager)
from fsqlfly.version_manager.manager.init import (ConnectorInitTransformManager, HiveInitTransformManager,
                                                  ListInitJobManager)
from fsqlfly.version_manager.clean_manager import (ConnectionCleanManager, ConnectorCleanManager)
from fsqlfly.version_manager.generator import (BaseResourceGenerator, SinkResourceGenerator,
                                               CanalResourceGenerator, SystemConnectorGenerator)


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
            return obj.target
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
            return SystemConnectorGenerator(obj)
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


class CleanManagerFactory(BaseManagerFactory):
    @classmethod
    def is_support(cls, model: str, obj: DBT) -> bool:
        return model in (PageModel.connector, PageModel.connection)

    @classmethod
    def build(cls, obj: DBT, dao: Dao) -> BaseVersionManager:
        if isinstance(obj, Connection):
            return ConnectionCleanManager(obj, dao)
        elif isinstance(obj, Connector):
            return ConnectorCleanManager(obj, dao)

        raise NotImplementedError("Not Support {} in CleanManagerFactory".format(obj.as_dict()))


class InitManagerFactory(BaseManagerFactory):
    @classmethod
    def is_support(cls, model: str, obj: DBT) -> bool:
        return model == PageModel.connector

    @classmethod
    def build(cls, obj: Connector, dao: Dao) -> BaseVersionManager:
        assert isinstance(obj, Connector)
        if obj.target.type.code == FlinkConnectorType.hive:
            return HiveInitTransformManager(obj, dao)
        return ConnectorInitTransformManager(obj, dao)


class ListManagerFactory(BaseManagerFactory):
    @classmethod
    def is_support(cls, model: str, obj: DBT) -> bool:
        return model == PageModel.connector

    @classmethod
    def build(cls, obj: DBT, dao: Dao) -> BaseVersionManager:
        return ListInitJobManager(obj, dao)


class ManagerFactory:
    @classmethod
    def get_factory(cls, mode: str) -> Type[BaseManagerFactory]:
        if mode == PageModelMode.update:
            return UpdateManagerFactory
        elif mode == PageModelMode.clean:
            return CleanManagerFactory
        elif mode == PageModelMode.init:
            return InitManagerFactory
        elif mode == PageModelMode.list:
            return ListManagerFactory
        raise NotImplementedError("current not support {} - in ManagerFactory ".format(mode))

    @classmethod
    def get_manager(cls, model: str, mode: str, obj: DBT, dao: Dao) -> BaseVersionManager:
        factory = cls.get_factory(mode)
        return factory.get_manager(model, obj, dao)
