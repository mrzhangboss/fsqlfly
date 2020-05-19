import unittest
from unittest.mock import patch
from fsqlfly.db_helper import *
from fsqlfly.tests.base_test import FSQLFlyTestCase


class MyTestCase(FSQLFlyTestCase):
    def test_positive_delete(self):
        namespace = Namespace(name='iii')
        self.session.add(namespace)
        self.session.commit()

        t = Transform(name='test', sql='select 1;', namespace=namespace)
        self.session.add(t)
        self.session.commit()
        self.session.delete(namespace)
        self.session.commit()
        self.assertEqual(self.session.query(Transform).count(), 0)

    def get_create_object(self):
        connection = Connection(name='a', url='#', type='hive', connector='text')
        schema = SchemaEvent(name='test', connection=connection, version=1)
        schema2 = SchemaEvent(name='test2', connection=connection, version=2)
        r_name = ResourceName(name='b', full_name='a.b', connection=connection, schema_version=schema)
        t_name = ResourceTemplate(name='c', resource_name=r_name, type='both', full_name='a.b.c', connection=connection,
                                  schema_version=schema)
        v_name = ResourceVersion(name='d', template=t_name, full_name='a.b.c.d', connection=connection,
                                 resource_name=r_name, schema_version=schema)
        return connection, schema, schema2, r_name, t_name, v_name

    def test_positive_delete_connection(self):
        connection, schema, schema2, r_name, t_name, v_name = self.get_create_object()

        self.session.add_all([connection, schema, schema2, r_name, t_name, v_name])
        self.session.commit()
        self.session.delete(connection)
        self.session.commit()
        self.assertEqual(self.session.query(ResourceName).count(), 0)
        self.assertEqual(self.session.query(Connection).count(), 0)

        self.assertEqual(self.session.query(ResourceVersion).count(), 0)
        self.assertEqual(self.session.query(ResourceTemplate).count(), 0)
        self.assertEqual(self.session.query(SchemaEvent).count(), 0)

    def test_positive_delete_connection_by_db_helper(self):
        connection, schema, schema2, r_name, t_name, v_name = self.get_create_object()

        self.session.add_all([connection, schema, schema2, r_name, t_name, v_name])
        self.session.commit()
        self.assertEqual(self.session.query(Connection).count(), 1)
        DBSession.init_engine(self.engine)
        with patch.object(settings, 'FSQLFLY_SAVE_MODE_DISABLE', True):
            res = DBDao.delete('connection', pk=connection.id)
        self.assertEqual(res.success, True)
        self.session.close()
        self.session = self.get_session()
        self.assertEqual(self.session.query(Connection).count(), 0)
        self.assertEqual(self.session.query(ResourceName).count(), 0)
        self.assertEqual(self.session.query(ResourceVersion).count(), 0)
        self.assertEqual(self.session.query(ResourceTemplate).count(), 0)
        self.assertEqual(self.session.query(SchemaEvent).count(), 0)

    def test_positive_delete_other(self):
        connection, schema, schema2, r_name, t_name, v_name = self.get_create_object()

        self.session.add_all([connection, schema, schema2, r_name, t_name, v_name])
        self.session.commit()
        self.session.delete(schema)

        self.session.commit()
        self.assertEqual(self.session.query(Connection).count(), 1)
        self.assertEqual(self.session.query(ResourceName).count(), 0)
        self.assertEqual(self.session.query(Connection).count(), 1)

        self.assertEqual(self.session.query(ResourceVersion).count(), 0)
        self.assertEqual(self.session.query(ResourceTemplate).count(), 0)
        self.assertEqual(self.session.query(SchemaEvent).count(), 1)

    def test_get_connection_and_resource_name_config(self):
        connection_config = """
[jdbc]
insert_primary_key = false

        """
        resource_name_config = """
[jdbc]
insert_primary_key = true
        """
        connection = Connection(name='a', url='#', type='hive', connector='text', config=connection_config)
        schema = SchemaEvent(name='test', connection=connection)
        r_name = ResourceName(name='b', full_name='a.b', connection=connection, schema_version=schema,
                              config=resource_name_config)
        self.assertTrue(not r_name.get_config('add_read_partition_key', 'jdbc', bool))
        self.assertTrue(not r_name.get_config('add_read_partition_key', 'jdbc', bool))
        self.assertEqual(connection.get_config('read_partition_num', 'jdbc', int), 50)
        self.assertTrue(r_name.get_config('example11') is None)

        self.assertTrue(r_name.get_config('insert_primary_key', 'jdbc', bool))
        self.assertTrue(not connection.get_config('insert_primary_key', 'jdbc', bool))


if __name__ == '__main__':
    unittest.main()
