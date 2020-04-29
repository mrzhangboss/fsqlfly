# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import unittest
from unittest.mock import patch, Mock
from fsqlfly.connection_manager import NameFilter, DatabaseManager, HiveManager, ElasticSearchManager, HBaseManager


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
        mn = DatabaseManager('mysql+pymysql://root:password@localhost:3306/fsqlfly', name_filter)

        mn.update()

    def test_hive_manager(self):
        name_filter = NameFilter('test\.alltypes')
        mn = HiveManager('hive://localhost:10000/default', name_filter)

        mn.update()

    def test_elasticsearch_manager(self):
        name_filter = NameFilter()
        mn = ElasticSearchManager('http://localhost:9200', name_filter)

        mn.update()

    def test_hbase_manager(self):
        name_filter = NameFilter()
        mn = HBaseManager('127.0.0.1:9090', name_filter)

        mn.update()


if __name__ == '__main__':
    unittest.main()
