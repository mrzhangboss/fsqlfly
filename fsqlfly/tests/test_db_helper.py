# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import unittest
from unittest.mock import patch, Mock
from fsqlfly.db_helper import DBDao
from fsqlfly.common import RespCode


class MyTestCase(unittest.TestCase):
    def test_not_support(self):
        s_m = 'connection'
        with self.assertRaises(TypeError):
            DBDao.update(1, model=s_m, obj=dict())

        self.assertEqual(DBDao.update('ttttasdf', 1, dict()).success, False)
        self.assertEqual(DBDao.update('ttttasdf', pk=1, obj=dict()).success, False)
        self.assertEqual(DBDao.update(model='ttttasdf', pk=1, obj=dict()).success, False)
        self.assertEqual(DBDao.update(model='ttttasdf', pk=1, obj=dict()).success, False)

        self.assertEqual(DBDao.update(model=s_m, pk=1, obj=dict()).success, False)

        self.assertEqual(DBDao.get('ttttasdf').code, RespCode.APIFail.code)
        self.assertEqual(DBDao.get('ttttasdf').success, False)


if __name__ == '__main__':
    unittest.main()
