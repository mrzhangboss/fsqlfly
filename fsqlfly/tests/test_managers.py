# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import unittest
from unittest.mock import patch, Mock
from fsqlfly.db_helper import Connector
from fsqlfly.connection_manager import *
from sqlalchemy import create_engine, event


class NameFilterTest(unittest.TestCase):
    def test_no_args(self):
        flt = NameFilter()
        self.assertTrue('asdf.csdfd' in flt)

    def test_with_args(self):
        flt = NameFilter('.*', 'ab\..*')
        self.assertTrue('abc.eff' in flt)
        self.assertTrue('ab.eff' not in flt)

        flt = NameFilter('ab[cde]?\..*', 'ab\..*')
        self.assertTrue('abc.eff' in flt)
        self.assertTrue('ab.eff' not in flt)
        self.assertTrue('abd.eff' in flt)
        self.assertTrue('abee.eff' not in flt)

        flt = NameFilter('.*\.alltypes')

        self.assertTrue('abc.alltypes' in flt)
        self.assertTrue('abc.lltypes' not in flt)
        self.assertTrue('abc.alltype' not in flt)


class ManagerTest(unittest.TestCase):
    def test_db_manager(self):
        name_filter = NameFilter('.*\.alltypes')

        mn = DatabaseManager('mysql+pymysql://root:password@localhost:3306/fsqlfly', name_filter, 'db')

        mn.update()

    def test_hive_manager(self):
        name_filter = NameFilter('test\.alltypes')
        mn = HiveManager('hive://localhost:10000/default', name_filter, 'hive')

        mn.update()

    def test_elasticsearch_manager(self):
        name_filter = NameFilter()
        mn = ElasticSearchManager('http://localhost:9200', name_filter, 'elasticsearch')

        mn.update()

    def test_hbase_manager(self):
        name_filter = NameFilter()
        mn = HBaseManager('127.0.0.1:9090', name_filter, 'hbase')
        mn.update()

    def setUp(self) -> None:
        self.sqlite_url = 'sqlite:///test.sqlite3'
        engine = create_engine(self.sqlite_url, echo=True)
        event.listen(engine, 'connect', lambda con, _: con.execute('pragma foreign_keys=ON'))
        DBSession.init_engine(engine)
        DBDao.delete_all_tables(True)
        DBDao.create_all_tables()
        self.engine = engine

    def test_run_with_connection(self):
        connection_args = [
            (self.sqlite_url, 'db', '')
        ]
        for url, typ, connector in connection_args:
            connection = Connection(name='a', url=url, type=typ, connector=connector)
            session = DBSession.get_session()
            session.add(connection)
            session.commit()
            res = ManagerHelper.update('connection', str(connection.id))
            self.assertTrue(res.success)
            self.assertTrue(session.query(SchemaEvent).count() > 0)
            self.assertTrue(session.query(ResourceName).count() > 0)
            self.assertTrue(session.query(ResourceTemplate).count() > 0)
            self.assertTrue(session.query(ResourceVersion).count() > 0)
            self.assertTrue(session.query(ResourceVersion).filter(ResourceVersion.cache.isnot(None)).count() > 0)
            session.close()

    def test_update_canal_connector(self):
        db = Connection(name='db', url='sqlite:///test.sqlite3', type='db', connector='')
        kafka = Connection(name='kafka', url='localhost:9092', type='kafka', connector='')
        session = DBSession.get_session()
        session.add_all([db, kafka])
        session.commit()
        config = """[canal]
mode = insert,update
        
        """
        connector = Connector(name='example', type='canal', source_id=db.id, target_id=kafka.id, config=config)
        session.add(connector)
        session.commit()

        res = ManagerHelper.update('connector', connector.id)
        self.assertTrue(res.success)

        self.assertTrue(session.query(SchemaEvent).count() > 0)



if __name__ == '__main__':
    unittest.main()
