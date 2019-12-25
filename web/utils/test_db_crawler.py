import attr
import pickle
import json
from utils.db_crawler import Crawler
from pprint import pprint
from web.settings import ENV
import unittest


class MyTestCase(unittest.TestCase):

    def test_mysql(self):
        self.test_mysql_url = ENV('TEST_MYSQL_CONNECTION_URL')
        if self.test_mysql_url is None:
            self.assertEqual(True, True)
        crawler = Crawler()
        cache = crawler.get_cache(self.test_mysql_url, 'ms', 'mysql')
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None




if __name__ == '__main__':
    unittest.main()
