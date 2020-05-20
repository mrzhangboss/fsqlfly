# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import unittest
from fsqlfly.version_manager import *
from fsqlfly.common import *
from fsqlfly.version_manager.helpers.manager import ManagerHelper
from fsqlfly.tests.base_test import FSQLFlyTestCase
from fsqlfly.settings import ENV

TEST_HIVE_SERVER2_URL = ENV('TEST_HIVE_SERVER2_URL', 'hive://localhost:10000')


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


class ManagerTest(FSQLFlyTestCase):
    def test_manager_helper_with_api_error(self):
        self.assertEqual(ManagerHelper.run(PageModel.connector, 'fake-mode', '1').success, False)

    def test_manager_helper_mode_not_support(self):
        con = self.init_test_connection()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(ManagerHelper.run(PageModel.connection, 'fake-mode', con.id).success, False)

    def test_manager_update_connection(self):
        con = self.init_test_connection()
        res = ManagerHelper.run(PageModel.connection, PageModelMode.update, con.id)
        print(res.msg)
        self.assertEqual(res.success, True)

    def test_manager_update_connector(self):
        connector = self.init_test_connector()
        res = ManagerHelper.run(PageModel.connector, PageModelMode.update, connector.id)
        print(res.msg)
        self.assertEqual(res.success, True)
        c = self.session.query(ResourceVersion).join(ResourceVersion.connection).filter(
            Connection.id == connector.target.id).count()
        self.assertTrue(c > 0)

    def test_manager_update_connector_with_hive_fail(self):
        connector = self.init_test_connector(FlinkConnectorType.hive)
        res = ManagerHelper.run(PageModel.connector, PageModelMode.update, connector.id)
        self.assertEqual(res.success, False)

    def test_manager_connection_clean(self):
        self.test_manager_update_connection()
        res = ManagerHelper.run(PageModel.connection, PageModelMode.clean, 1)
        self.assertEqual(res.success, True)
        self.assertEqual(self.session.query(ResourceVersion).count(), 0)
        self.assertEqual(self.session.query(ResourceTemplate).count(), 0)
        self.assertEqual(self.session.query(ResourceName).count(), 0)

    def test_manager_connector_clean(self):
        self.test_manager_update_connector()
        res = ManagerHelper.run(PageModel.connection, PageModelMode.clean, 1)
        self.assertEqual(res.success, True)
        res = ManagerHelper.run(PageModel.connection, PageModelMode.clean, 2)
        self.assertEqual(res.success, True)
        c = self.session.query(Transform).count()
        self.assertEqual(c, 0)

    def test_manager_init_not_support(self):
        con = self.init_test_connection()
        res = ManagerHelper.run(PageModel.connection, PageModelMode.init, con.id)
        self.assertEqual(res.success, False)

    def test_manager_init(self):
        con = self.init_test_connector(typ=FlinkConnectorType.hive, c_type=ConnectorType.system)

        res = ManagerHelper.run(PageModel.connection, PageModelMode.update, con.source.id)
        print(res.msg)
        self.assertEqual(res.success, True)

        res = ManagerHelper.run(PageModel.connector, PageModelMode.update, con.id)
        print(res.msg)
        self.assertEqual(res.success, True)

        res = ManagerHelper.run(PageModel.connector, PageModelMode.init, con.id)
        print(res.msg)
        self.assertEqual(res.success, False)

    def init_test_connection(self):
        from fsqlfly.settings import FSQLFLY_DB_URL
        con = Connection(name='fake', url=FSQLFLY_DB_URL, type=FlinkConnectorType.jdbc, connector='', include='sample\..*')
        self.session.add(con)
        self.session.commit()
        return con

    def init_test_connector(self, typ=FlinkConnectorType.kafka, c_type=ConnectorType.canal):
        con = self.init_test_connection()
        k_connector = """
        type: kafka
        version: universal     # required: valid connector versions are    "0.8", "0.9", "0.10", "0.11", and "universal"
        properties:
          zookeeper.connect: localhost:2181  # required: specify the ZooKeeper connection string
          bootstrap.servers: localhost:9092  # required: specify the Kafka server connection string
          group.id: testGroup                # optional: required in Kafka consumer, specify consumer group

        topic: {{ resource_name.database }}__{{ resource_name.name }}__{{ version.name }}        
                """
        url = 'xxx'
        if typ == FlinkConnectorType.hive:
            url = TEST_HIVE_SERVER2_URL

        sink = Connection(name='sink', url=url, type=typ, connector=k_connector, include='sample\..*')
        connector = Connector(name='connector', type=c_type, source=con, target=sink)
        self.session.add_all([sink, connector])
        self.session.commit()
        return connector

    def test_db_manager(self):
        name_filter = NameFilter('.*\.alltypes')

        mn = DatabaseManager('mysql+pymysql://root:password@localhost:3306/fsqlfly', name_filter, 'db')

        mn.update()

    def test_hive_manager(self):
        name_filter = NameFilter('test\.alltypes')
        mn = HiveManager(TEST_HIVE_SERVER2_URL, name_filter, 'hive')

        mn.update()

    def test_elasticsearch_manager(self):
        name_filter = NameFilter()
        mn = ElasticSearchManager('http://localhost:9200', name_filter, 'elasticsearch')

        mn.update()

    def test_hbase_manager(self):
        name_filter = NameFilter()
        mn = HBaseManager('127.0.0.1:9090', name_filter, 'hbase')
        mn.update()


if __name__ == '__main__':
    unittest.main()
