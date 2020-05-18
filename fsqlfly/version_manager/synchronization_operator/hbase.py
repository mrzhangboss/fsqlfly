from typing import List

from fsqlfly.common import SchemaContent, SchemaField, BlinkHiveSQLType
from fsqlfly.version_manager.synchronization import BaseSynchronizationOperator


class HBaseSynchronizationOperator(BaseSynchronizationOperator):
    def run(self) -> List[SchemaContent]:
        assert 'hbase' == self.db_type
        import happybase
        host, port = self.connection_url.split(':')
        connection = happybase.Connection(host, int(port), autoconnect=True)
        schemas = []
        for x in connection.tables():
            tab = x.decode()
            table = connection.table(tab)
            schema = SchemaContent(name=tab, type=self.db_type)
            fields = []
            for fm in table.families():
                fields.append(SchemaField(name=fm.decode(), type=BlinkHiveSQLType.BYTES, nullable=True))
            schema.fields.extend(fields)
            schemas.append(schema)
        return schemas