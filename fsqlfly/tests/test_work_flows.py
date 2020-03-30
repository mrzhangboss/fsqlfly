import unittest
from fsqlfly.workflow import run_debug_transform
from terminado import NamedTermManager
from fsqlfly.tests.base_test import BaseTestCase


class MyTestCase(BaseTestCase):
    def test_something(self):
        run_debug_transform(dict(), NamedTermManager(shell_command=['ls']))


if __name__ == '__main__':
    unittest.main()
