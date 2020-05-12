import unittest
from fsqlfly.db_helper import *
from fsqlfly.tests.base_test import FSQLFlyTestCase

class MyTestCase(FSQLFlyTestCase):
    def test_something(self):
        connection = Connection(name='a', url='#', type='hive', connector='text')
        schema = SchemaEvent(name='test', connection=connection, version=1)
        schema2 = SchemaEvent(name='test2', connection=connection, version=2)
        r_name = ResourceName(name='b', full_name='a.b', connection=connection, schema_version=schema)
        t_name = ResourceTemplate(name='c', resource_name=r_name, type='both', full_name='a.b.c', connection=connection,
                                  schema_version=schema)
        v_name = ResourceVersion(name='d', template=t_name, full_name='a.b.c.d', connection=connection,
                                 resource_name=r_name, schema_version=schema)
        session = DBSession.get_session()

        session.add_all([connection, schema, schema2, r_name, t_name, v_name])


if __name__ == '__main__':
    unittest.main()
