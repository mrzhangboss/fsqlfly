import unittest
import importlib
from fsqlfly import settings
import fsqlfly.models
from peewee import SqliteDatabase, IntegrityError
from unittest.mock import patch


def gen_mock(f):
    def _gen(*args, **kwargs):
        with patch('fsqlfly.settings.DATABASE', SqliteDatabase(':memory:')):
            return f(*args, **kwargs)

    return _gen


class BaseTestCase(unittest.TestCase):
    @gen_mock
    def setUp(self) -> None:
        fsqlfly.models.create_all_tables()

    @gen_mock
    def tearDown(self) -> None:
        fsqlfly.models.delete_all_tables(force=True)


if __name__ == '__main__':
    unittest.main()
