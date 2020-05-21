from typing import List, Type

from fsqlfly.common import NameFilter, SchemaContent, FlinkConnectorType
from fsqlfly.db_models import Connection
from fsqlfly.version_manager.synchronization import BaseSynchronizationOperator
from fsqlfly.version_manager.synchronization_operator import (JDBCSynchronizationOperator, HiveSynchronizationOperator,
                                                              ElasticsearchSynchronizationOperator,
                                                              FilesystemSynchronizationOperator,
                                                              KafkaSynchronizationOperator)


class SynchronizationHelper:
    @classmethod
    def get_factory(cls, c_type: str) -> Type[BaseSynchronizationOperator]:
        if c_type == FlinkConnectorType.jdbc:
            return JDBCSynchronizationOperator
        elif c_type == FlinkConnectorType.hive:
            return HiveSynchronizationOperator
        elif c_type == FlinkConnectorType.elasticsearch:
            return ElasticsearchSynchronizationOperator
        elif c_type == FlinkConnectorType.filesystem:
            return FilesystemSynchronizationOperator
        elif c_type == FlinkConnectorType.kafka:
            return KafkaSynchronizationOperator
        else:
            raise NotImplementedError("Not Support {} schema parser".format(c_type))

    @classmethod
    def synchronize(cls, connection: Connection, name_filter: NameFilter) -> List[SchemaContent]:
        c_type = connection.type.code
        factory = cls.get_factory(c_type)
        operator = factory(connection, name_filter)
        return operator.run()
