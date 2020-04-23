import unittest
import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from fsqlfly.db_models import *


class MyTestCase(unittest.TestCase):
    def _fk_pragma_on_connect(self, dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    def setUp(self) -> None:
        # engine = sa.create_engine('sqlite://', echo=True)
        engine = sa.create_engine('mysql+pymysql://root:password@localhost:3306/test', echo=True)
        # event.listen(engine, 'connect', self._fk_pragma_on_connect)
        DBSession = sessionmaker(bind=engine)

        delete_all_tables(engine, force=True)
        create_all_tables(engine)
        self.session = DBSession()

    def tearDown(self) -> None:
        self.session.commit()
        self.session.close()

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

    def test_positive_delete_many(self):
        connection = Connection(name='a', url='#', type='hive', connector='text')
        schema = SchemaEvent(name='test', connection=connection, version=1, type='hive')
        schema2 = SchemaEvent(name='test2', connection=connection, version=2, type='hive')
        r_name = ResourceName(name='b', full_name='a.b', connection=connection, schema_version=schema)
        t_name = ResourceTemplate(name='c', resource_name=r_name, full_name='a.b.c', connection=connection,
                                  schema_version=schema)
        v_name = ResourceVersion(name='d', template=t_name, full_name='a.b.c.d', connection=connection,
                                 resource_name=r_name, schema_version=schema)

        self.session.add_all([connection, schema, schema2, r_name, t_name, v_name])
        self.session.commit()
        self.session.delete(schema)

        self.session.commit()
        self.assertEqual(self.session.query(ResourceName).count(), 0)
        self.assertEqual(self.session.query(Connection).count(), 1)

        self.assertEqual(self.session.query(ResourceVersion).count(), 0)
        self.assertEqual(self.session.query(ResourceTemplate).count(), 0)
        self.assertEqual(self.session.query(SchemaEvent).count(), 1)


if __name__ == '__main__':
    unittest.main()
