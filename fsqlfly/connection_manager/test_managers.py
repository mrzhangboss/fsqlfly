# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import unittest
from unittest.mock import patch, Mock
from fsqlfly.connection_manager import NameFilter, DatabaseManager


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


if __name__ == '__main__':
    unittest.main()
