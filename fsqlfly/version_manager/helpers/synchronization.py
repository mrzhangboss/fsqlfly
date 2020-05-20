from typing import List

from fsqlfly.common import NameFilter, SchemaContent, FlinkConnectorType
from fsqlfly.db_models import Connection
from fsqlfly.version_manager.synchronization_operator import (JDBCSynchronizationOperator, HiveSynchronizationOperator,
                                                              ElasticsearchSynchronizationOperator)


class SynchronizationHelper:
    @classmethod
    def synchronize(cls, connection: Connection, name_filter: NameFilter) -> List[SchemaContent]:
        c_type = connection.type.code
        if c_type == FlinkConnectorType.jdbc:
            operator = JDBCSynchronizationOperator(connection, name_filter)
        elif c_type == FlinkConnectorType.hive:
            operator = HiveSynchronizationOperator(connection, name_filter)
        elif c_type == FlinkConnectorType.elasticsearch:
            operator = ElasticsearchSynchronizationOperator(connection, name_filter)
        else:
            raise NotImplementedError("Not Support {} schema parser".format(c_type))
        return operator.run()
