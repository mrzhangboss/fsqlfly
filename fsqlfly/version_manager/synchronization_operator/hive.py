from typing import Optional

from logzero import logger
from sqlalchemy import TypeDecorator, VARCHAR, CHAR, String, BINARY

from fsqlfly.common import BlinkHiveSQLType
from fsqlfly.version_manager.synchronization import SqlalchemySynchronizationOperator


class HiveSynchronizationOperator(SqlalchemySynchronizationOperator):
    use_comment = False
    use_primary = False
    support_type = []

    hive_types = set(list(x for x in dir(BlinkHiveSQLType) if not x.startswith('__')))

    def convert_flink_type(self, typ: TypeDecorator) -> Optional[str]:
        name = None
        types = BlinkHiveSQLType
        str_name = str(typ)

        if isinstance(typ, (VARCHAR, CHAR, String)):
            name = types.STRING
        elif isinstance(typ, BINARY):
            name = types.BYTES
        elif str_name in self.hive_types:
            name = str_name
        if name is None:
            logger.error("Not Support Current Type in DB {}".format(str(typ)))
            return None
        return name
