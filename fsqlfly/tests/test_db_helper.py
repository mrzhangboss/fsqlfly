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

    def test_crud(self):
        obj = dict(name='example', type='hive', url='xx', is_locked=False, connector='')
        c = 'connection'
        self.assertEqual(DBDao.create(model=c, obj=obj).success, True)
        data = DBDao.get(model=c).data
        pk = data[0]['id']
        self.assertEqual(len(data), 1)
        obj['is_locked'] = True
        self.assertEqual(DBDao.update(model=c, pk=pk, obj=obj).success, True)
        self.assertEqual(DBDao.get(model=c).data[0]['is_locked'], True)
        d_res = DBDao.delete(model=c, pk=data[0]['id'])
        self.assertEqual(d_res.success, True)
        self.assertEqual(d_res.data, pk)
        self.assertEqual(len(DBDao.get(model=c).data), 0)


    def test_bulk_insert(self):
        data = []
        c = 'connection'
        num = 100
        for i in range(num):
            data.append(Connection(**dict(name=f'example{i}', type='hive', url='xx', is_locked=False, connector='')))
        self.assertEqual(DBDao.bulk_insert(data).data, num)


if __name__ == '__main__':
    unittest.main()
