import re
import unittest
from fsqlfly.common import *


class MyTestCase(unittest.TestCase):
    def test_key_num(self):
        self.assertTrue('key' not in FlinkTableType.keys())
        self.assertEqual(len(FlinkTableType.keys()), 5)

    def test_page_mode_regex(self):
        self.assertEqual(len(PageModelMode.keys()), 4)
        p = re.compile(PageModelMode.regex())
        for x in PageModelMode.keys():
            self.assertTrue(p.match(x))


if __name__ == '__main__':
    unittest.main()
