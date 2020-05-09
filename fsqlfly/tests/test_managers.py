# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import unittest
from unittest.mock import patch, Mock
from fsqlfly.db_helper import Connector
from fsqlfly.connection_manager import *
from sqlalchemy import create_engine, event, func


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
        from fsqlfly.settings import FSQLFLY_DB_URL
        db = Connection(name='db', url=FSQLFLY_DB_URL, type='db', connector='', include='sample.*')
        k_connector = """
type: kafka
version: universal     # required: valid connector versions are    "0.8", "0.9", "0.10", "0.11", and "universal"
properties:
  zookeeper.connect: localhost:2181  # required: specify the ZooKeeper connection string
  bootstrap.servers: localhost:9092  # required: specify the Kafka server connection string
  group.id: testGroup                # optional: required in Kafka consumer, specify consumer group

topic: {{ resource_name.database }}__{{ resource_name.name }}__{{ version.name }}        
        """
        kafka = Connection(name='kafka', url='localhost:9092', type='kafka', connector=k_connector)
        session = DBSession.get_session()
        session.add_all([db, kafka])
        session.commit()
        config = """[canal]
mode = insert,update
canal_host: localhost
canal_port: 11111
canal_username: root
canal_password: password
canal_client_id: 11021
canal_destination: example
canal_filter: .*\..*        
        """
        connector = Connector(name='example', type='canal', source_id=db.id, target_id=kafka.id, config=config)
        session.add(connector)
        session.commit()

        res = ManagerHelper.update('connector', connector.id)
        self.assertTrue(res.success)

        self.assertTrue(session.query(SchemaEvent).count() > 0)
        res = session.query(ResourceVersion.template_id, func.count(ResourceVersion.id)).filter(
            ResourceVersion.name != 'latest').group_by(ResourceVersion.template_id).all()
        self.assertTrue(all(map(lambda x: x[1] == 2, res)))

        connector_id = connector.id
        session.close()
        from fsqlfly.contrib.canal import Consumer

        Consumer.build(connector_id).run()


if __name__ == '__main__':
    unittest.main()
