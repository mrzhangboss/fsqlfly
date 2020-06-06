from typing import Tuple, List, Optional
from logzero import logger
from itertools import chain
from sqlalchemy import create_engine, inspect, TypeDecorator
from sqlalchemy.sql.sqltypes import INTEGER, SMALLINT, BIGINT
from fsqlfly.db_helper import Connection
from fsqlfly.common import NameFilter, SchemaContent, SchemaField, FlinkConnectorType


class BaseSynchronizationOperator:
    def __init__(self, connection: Connection, name_filter: NameFilter):
        self._connection = connection
        self.need_tables = name_filter

    def run(self) -> List[SchemaContent]:
        raise NotImplementedError

    @property
    def db_type(self) -> str:
        return self._connection.type.code

    @property
    def connection_url(self):
        return self._connection.url


class SqlalchemySynchronizationOperator(BaseSynchronizationOperator):
    def __init__(self, connection: Connection, name_filter: NameFilter):
        super(SqlalchemySynchronizationOperator, self).__init__(connection, name_filter)
        self.engine = create_engine(self.connection_url)
        self.inspection = inspect(self.engine)

    use_comment = True
    use_primary = True

    def convert_flink_type(self, typ: TypeDecorator) -> Optional[str]:
        raise NotImplementedError

    def get_table_comment(self, tb: str, db: str):
        comment = None
        if self.use_comment:
            try:
                comment = self.inspection.get_table_comment(table_name=tb, schema=db)['text']
            except NotImplementedError as err:
                print('meet ', err)

        return comment

    def _warp(self, s: str) -> str:
        if self.db_type == FlinkConnectorType.hive:
            return f'`{s}`'
        return s

    def run(self) -> List[SchemaContent]:
        db_list = self.inspection.get_schema_names()
        update_tables = self.get_update_tables(db_list)

        schemas = []

        for db, tb in update_tables:
            schema = SchemaContent(name=tb, database=db, comment=self.get_table_comment(tb, db), type=self.db_type)
            columns = self.inspection.get_columns(table_name=self._warp(tb), schema=self._warp(db))
            self.set_primary_info(schema, columns, db, tb)

            fields = []
            for x in columns:
                field = SchemaField(name=x['name'], type=self.convert_flink_type(x['type']),
                                    nullable=x['nullable'], autoincrement=x.get('autoincrement'))
                if field.type is None:
                    logger.error(
                        "Not Add Column {} in {}.{} current not support : {}".format(field.name, schema.database,
                                                                                     schema.name, str(x['type'])))
                else:
                    fields.append(field)

            schema.fields.extend(fields)

            schemas.append(schema)
        return schemas

    def get_update_tables(self, db_list) -> List[Tuple[str, str]]:
        update_tables = []
        for db in db_list:
            for tb in chain(self.inspection.get_table_names(db), self.inspection.get_view_names(db)):
                full_name = f'{db}.{tb}'
                if full_name in self.need_tables:
                    update_tables.append((db, tb))
        return update_tables

    def set_primary_info(self, schema: SchemaContent, columns: List[dict], db: str, tb: str):
        primary = self.inspection.get_primary_keys(tb, db) if self.use_primary else None
        if primary and len(primary) == 1:
            schema.primary_key = primary[0]
            column = list(filter(lambda x: x['name'] == primary[0], columns))[0]
            if isinstance(column['type'], (INTEGER, SMALLINT, BIGINT)):
                schema.partitionable = True


class DBSynchronizationOperator(BaseSynchronizationOperator):
    def run(self) -> List[SchemaContent]:
        res = []
        for resource_name in self._connection.resource_names:
            if resource_name.db_name in self.need_tables:
                res.append(resource_name.schema_version.to_schema_content())
        return res
