import unittest
import random
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from fsqlfly.db_helper import *


class FSQLFlyTestCase(unittest.TestCase):
    def _fk_pragma_on_connect(self, dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    def setUp(self) -> None:
        engine = sa.create_engine('sqlite://', echo=True)
        event.listen(engine, 'connect', self._fk_pragma_on_connect)

        DBSession.init_engine(engine)
        delete_all_tables(engine, force=True)
        create_all_tables(engine)
        self.DBSession = DBSession
        self.session = self.get_session()
        self.engine = engine

    def get_session(self):
        return self.DBSession.get_session()

    def tearDown(self) -> None:
        self.session.close()


if __name__ == '__main__':
    unittest.main()
