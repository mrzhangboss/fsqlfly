# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from fsqlfly.db_helper import *
import sqlalchemy as sa
import unittest
from unittest.mock import patch, Mock
from fsqlfly.common import RespCode, DBRes
from sqlalchemy import event


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        engine = sa.create_engine('sqlite://', echo=True)
        event.listen(engine, 'connect', lambda con, _: con.execute('pragma foreign_keys=ON'))
        DBSession.init_engine(engine)
        delete_all_tables(engine, True)
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
        from fsqlfly import settings
        with patch.object(settings, 'FSQLFLY_SAVE_MODE_DISABLE', False):
            d_res = DBDao.delete(model=c, pk=data[0]['id'])
            self.assertEqual(d_res.success, False)
        with patch.object(settings, 'FSQLFLY_SAVE_MODE_DISABLE', True):
            d_res = DBDao.delete(model=c, pk=data[0]['id'])
            self.assertEqual(d_res.success, True)
        self.assertEqual(d_res.data, pk)
        self.assertEqual(len(DBDao.get(model=c).data), 0)

    def test_get_with_other_filter(self):
        name1, name2 = 'example1', 'example2'
        obj1 = dict(name=name1, type='hive', url='xx1', is_locked=False, connector='')
        obj2 = dict(name=name2, type='hbase', url='xx1', is_locked=False, connector='')
        c = 'connection'
        self.assertEqual(DBDao.create(model=c, obj=obj1).success, True)
        self.assertEqual(DBDao.create(model=c, obj=obj2).success, True)
        self.assertEqual(len(DBDao.get(model=c).data), 2)
        self.assertEqual(len(DBDao.get(model=c, filter_=dict(name=name1)).data), 1)
        self.assertEqual(len(DBDao.get(model=c, filter_=dict(name=name1, type='hbase')).data), 0)
        self.assertEqual(len(DBDao.get(model=c, filter_=dict(id='1')).data), 1)

    def test_get_response_contain_id(self):
        name1, name2 = 'example1', 'example2'
        obj1 = dict(name=name1, type='hive', url='xx1', is_locked=False, connector='')
        c = 'connection'
        res = DBDao.create(model=c, obj=obj1)
        self.assertEqual('id' in res.data, True)
        obj2 = dict(name=name1, database='aa', is_locked=False, connection_id=res.data['id'], full_name='xxxxxx')
        res = DBDao.create(model='name', obj=obj2)
        self.assertEqual('id' in res.data, True)

    def test_bulk_insert(self):
        data = []
        c = 'connection'
        num = 100
        for i in range(num):
            data.append(Connection(**dict(name=f'example{i}', type='hive', url='xx', is_locked=False, connector='')))
        self.assertEqual(DBDao.bulk_insert(data).data, num)

    def test_update_reset_default(self):
        connection = Connection(name='example', type='hive', url='xx', is_locked=True, connector='')
        r_name = ResourceName(name='r_name', connection=connection, full_name='example.r_name')
        t1_name = ResourceTemplate(name='t1', type='sink', connection=connection, full_name='example.r1_name.t1',
                                   resource_name=r_name, is_default=True)
        t2_name = ResourceTemplate(name='t2', type='sink', connection=connection, full_name='example.r2_name.t2',
                                   resource_name=r_name, is_default=True)

        r2_name = ResourceName(name='r2_name', connection=connection, full_name='example.r2_name')
        t3_name = ResourceTemplate(name='t3', type='sink', connection=connection, full_name='example.r1_name.t3',
                                   resource_name=r2_name, is_default=True)
        t4_name = ResourceTemplate(name='t4', type='sink', connection=connection, full_name='example.r2_name.t4',
                                   resource_name=r2_name, is_default=True)
        session = DBSession.get_session()
        session.add(connection)
        session.add(r_name)
        session.add(t1_name)
        session.add_all([r2_name, t3_name, t4_name])
        session.commit()

        session.add(t2_name)
        session.commit()
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.is_default == True).count(), 1)
        t1_name.is_default = True
        session.commit()
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.id == t1_name.id).first().is_default,
                         True)
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.id == t2_name.id).first().is_default,
                         False)
        t3_name.is_default = True
        session.commit()
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.id == t1_name.id).first().is_default,
                         True)
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.id == t2_name.id).first().is_default,
                         False)
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.id == t3_name.id).first().is_default,
                         True)
        self.assertEqual(session.query(ResourceTemplate).filter(ResourceTemplate.id == t4_name.id).first().is_default,
                         False)

    def test_upsert(self):
        connection = Connection(name='connection', connector='axx', url='abcde', type='hive')
        session = DBSession.get_session()
        connection = DBDao.save(connection, session=session)
        scheme1 = SchemaEvent(name='example', info='abc', database='hh', connection_id=connection.id)
        scheme1, inserted = DBDao.upsert_schema_event(scheme1, session=session)
        self.assertTrue(not isinstance(scheme1, DBRes))
        self.assertTrue(inserted)
        self.assertEqual(len(DBDao.get('schema').data), 1)
        scheme2 = SchemaEvent(name='example', info='abc', database='hh', connection_id=connection.id)
        scheme2, inserted = DBDao.upsert_schema_event(scheme2, session=session)
        self.assertTrue(not inserted)
        self.assertTrue(isinstance(scheme2, SchemaEvent))
        data = DBDao.get('schema').data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].id, scheme2.id)
        self.assertEqual(data[0]['id'], scheme2.id)
        self.assertEqual(DBDao.get('schema').data[0]['version'], 0)

        resource_name = ResourceName(name='xxx', connection_id=connection.id, full_name='xxx')
        resource_name, inserted = DBDao.upsert_resource_name(resource_name, session=session)
        self.assertTrue(inserted)
        resource_name, inserted = DBDao.upsert_resource_name(resource_name, session=session)
        self.assertTrue(not inserted)
        self.assertEqual(len(DBDao.get('name').data), 1)

        template = ResourceTemplate(name='xxx', connection_id=connection.id, full_name='xxx',
                                    schema_version_id=scheme2.id, type='sink',
                                    resource_name_id=resource_name.id)
        template, inserted = DBDao.upsert_resource_template(template, session=session)
        self.assertTrue(inserted)
        template, inserted = DBDao.upsert_resource_template(template, session=session)
        self.assertTrue(not inserted)
        self.assertEqual(len(DBDao.get('template').data), 1)

        version = ResourceVersion(name='xxxx', connection_id=connection.id, full_name='xxx',
                                  schema_version_id=scheme2.id, template_id=template.id,
                                  resource_name_id=resource_name.id)

        version, inserted = DBDao.upsert_resource_version(version, session=session)
        DBDao.upsert_resource_version(version, session=session)
        self.assertTrue(inserted)
        self.assertEqual(len(DBDao.get('version').data), 1)

        version2 = ResourceVersion(name='xxxx', connection_id=connection.id, full_name='xxxaaa',
                                   config='xxx', template_id=template.id,
                                   schema_version_id=scheme2.id,
                                   resource_name_id=resource_name.id)

        new_version, inserted = DBDao.upsert_resource_version(version2, session=session)
        self.assertTrue(inserted)
        self.assertTrue(new_version.version > version.version)

        session.close()

    def test_clean(self):
        session = DBSession.get_session()

        connection1 = Connection(name='example1', type='hive', url='xx', is_locked=True, connector='')
        connection2 = Connection(name='example2', type='db', url='xx', is_locked=True, connector='')
        session.add_all([connection1, connection2])
        session.commit()
        connector = Connector(name='example', type='canal', source_id=connection1.id, target_id=connection2.id,
                              config='')
        session.add(connector)
        session.commit()
        transform = Transform(name='a', sql='', require='', connector_id=connector.id)
        session.add(transform)
        session.commit()
        res = DBDao.clean('connector', connector.id, session=session)
        self.assertTrue(res.success)
        self.assertEqual(session.query(Transform).count(), 0)

    def test_name2pk(self):
        session = DBSession.get_session()
        name = 'example1'
        connection1 = Connection(name=name, type='hive', url='xx', is_locked=True, connector='')
        session.add(connection1)
        session.commit()

        self.assertEqual(DBDao.name2pk('connection', name='example1'), connection1.id)
        with self.assertRaises(Exception):
            DBDao.name2pk('connection', name='example2')

if __name__ == '__main__':
    unittest.main()
