import unittest
import json
import importlib
from fsqlfly import settings
from peewee import SqliteDatabase, IntegrityError
import fsqlfly.models
from fsqlfly.tests.base_test import BaseTestCase


class MyTestCase(BaseTestCase):
    def test_namespace_unique(self):
        name = 'abcdd'
        sample = fsqlfly.models.Namespace.create(name=name)
        with self.assertRaises(IntegrityError):
            fsqlfly.models.Namespace.create(name=name)

    def test_model_to_dict(self):
        sample = fsqlfly.models.Namespace.create(name='name')
        self.assertTrue(isinstance(sample.to_dict(), dict))
        self.assertTrue(isinstance(json.dumps(sample.to_dict()), str))


if __name__ == '__main__':
    unittest.main()
