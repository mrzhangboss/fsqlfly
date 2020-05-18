from typing import Optional
from logzero import logger
from sqlalchemy import TypeDecorator
from fsqlfly.common import BlinkSQLType
from fsqlfly.version_manager.synchronization import SqlalchemySynchronizationOperator
from sqlalchemy.dialects.mysql.types import _StringType as M_STRING, BIT as M_BIT, TINYINT, DOUBLE as M_DOUBLE
from sqlalchemy.dialects.postgresql import (DOUBLE_PRECISION as P_DOUBLE, BIT as P_BIT, VARCHAR, CHAR, TEXT,
                                            JSON, BOOLEAN)
from sqlalchemy.sql.sqltypes import (DATE, _Binary, INTEGER, SMALLINT, BIGINT, FLOAT, DECIMAL,
                                     DATETIME,
                                     TIMESTAMP, TIME)


class JDBCSynchronizationOperator(SqlalchemySynchronizationOperator):
    use_comment = True
    use_primary = True

    def convert_flink_type(self, typ: TypeDecorator) -> Optional[str]:

        name = None
        types = BlinkSQLType
        if isinstance(typ, (M_STRING, VARCHAR, CHAR, TEXT, JSON)):
            name = types.STRING
        elif isinstance(typ, _Binary):
            name = types.BYTES
        elif isinstance(typ, BOOLEAN):
            name = types.BOOLEAN
        elif isinstance(typ, (TINYINT, SMALLINT, INTEGER)):
            name = types.INTEGER
        elif isinstance(typ, (P_BIT, M_BIT)):
            name = types.TINYINT
        elif isinstance(typ, BIGINT):
            name = types.BIGINT
        elif isinstance(typ, FLOAT):
            name = types.FLOAT
        elif isinstance(typ, (M_DOUBLE, P_DOUBLE)):
            name = types.DOUBLE
        elif isinstance(typ, DECIMAL):
            name = types.DECIMAL
        elif isinstance(typ, DATETIME) or isinstance(typ, TIMESTAMP):
            name = types.TIMESTAMP
        elif isinstance(typ, DATE):
            name = types.DATE
        elif isinstance(typ, TIME):
            name = types.TIME

        if name is None:
            logger.error("Not Support Current Type in DB {}".format(str(typ)))
            return None
        return name
