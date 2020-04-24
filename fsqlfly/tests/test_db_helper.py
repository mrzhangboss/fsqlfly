# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from fsqlfly.db_models import *
import sqlalchemy as sa
import unittest
from unittest.mock import patch, Mock
from fsqlfly.db_helper import DBDao, DBSession
from fsqlfly.common import RespCode, DBRes
from sqlalchemy import event


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        engine = sa.create_engine('sqlite://', echo=True)
        event.listen(engine, 'connect', lambda con, _: con.execute('pragma foreign_keys=ON'))
        DBSession.init_engine(engine)
        create_all_tables(engine)
        self.engine = engine

    def tearDown(self) -> None:
        delete_all_tables(self.engine, True)

    def test_not_support(self):
        s_m = 'connection'

        self.assertEqual(DBDao.update(model='asdfdf', pk=1, obj=dict()).success, False)

        self.assertEqual(DBDao.update('ttttasdf', 1, dict()).success, False)
        self.assertEqual(DBDao.update('ttttasdf', pk=1, obj=dict()).success, False)
        self.assertEqual(DBDao.update(model='ttttasdf', pk=1, obj=dict()).success, False)
        self.assertEqual(DBDao.update(model='ttttasdf', pk=1, obj=dict()).success, False)

        self.assertEqual(DBDao.get('ttttasdf').code, RespCode.APIFail.code)
        self.assertEqual(DBDao.get('ttttasdf').success, False)

    def test_not_init_session(self):
        DBSession.init_engine(None)
        with self.assertRaises(AssertionError):
            self.assertEqual(DBDao.update(model='connection', pk=1, obj=dict()), DBRes.not_found())

    def test_not_found(self):
        self.assertEqual(DBDao.update(model='connection', pk=1, obj=dict()), DBRes.not_found())

    def test_cannot_update_because_lock(self):
        obj = Connection(name='example', type='hive', url='xx', is_locked=True, connector='')
        session = DBSession.get_session()
        session.add(obj)
        session.commit()
        c = 'connection'
        self.assertEqual(DBDao.update(model=c, pk=obj.id, obj=obj.as_dict()).success, False)
        obj.is_locked = False
        session.commit()
        self.assertEqual(DBDao.update(model=c, pk=obj.id, obj=obj.as_dict()).success, True)



if __name__ == '__main__':
    unittest.main()
