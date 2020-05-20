from abc import ABC
from typing import Union
from fsqlfly.db_helper import Connector
from fsqlfly.common import DBRes, ConnectorType
from fsqlfly.version_manager.base import BaseVersionManager
from fsqlfly.version_manager.dao import Dao


class InitManager(BaseVersionManager, ABC):
    def __init__(self, target: Connector, dao: Dao):
        self.target = target
        self.dao = dao

    def is_support(self) -> bool:
        return self.target.type.code == ConnectorType.system


class ConnectorInitTransformManager(InitManager):
    def run(self) -> DBRes:
        return DBRes()
