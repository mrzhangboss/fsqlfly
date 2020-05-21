from abc import ABC
from typing import Union
from fsqlfly.db_helper import Connection, Connector
from fsqlfly.common import DBRes, ConnectorType
from fsqlfly.version_manager.base import BaseVersionManager
from fsqlfly.version_manager.dao import Dao


class CleanManager(BaseVersionManager, ABC):
    def __init__(self, target: Union[Connector, Connection], dao: Dao):
        self.target = target
        self.dao = dao

    def is_support(self) -> bool:
        return True


class ConnectionCleanManager(CleanManager):
    def run(self) -> DBRes:
        return self.dao.clean_connection(self.target)


class ConnectorCleanManager(CleanManager):
    def is_support(self) -> bool:
        return self.target.type.code == ConnectorType.system

    def run(self) -> DBRes:
        return self.dao.clean_connector(self.target)
