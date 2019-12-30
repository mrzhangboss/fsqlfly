import attr
import pickle
import json
from utils.db_crawler import Crawler
from pprint import pprint
from web.settings import ENV
import unittest

NAME = 'TEST'


class MyTestCase(unittest.TestCase):

    def test_mysql(self):
        url = ENV('TEST_MYSQL_CONNECTION_URL')
        if url is None:
            return self.assertEqual(True, True)
        crawler = Crawler()
        cache = crawler.get_cache(url, 'ms', 'mysql', NAME)
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None

        cache2 = crawler.get_cache(url, 'ms', 'mysql', NAME, '.*\..*')
        self.assertEqual(len(cache.tables), len(cache2.tables))
        cache3 = crawler.get_cache(url, 'ms', 'mysql', NAME, None, '.*\..*')
        self.assertEqual(len(cache3.tables), 0)

    def test_hive(self):
        url = ENV('TEST_HIVE_CONNECTION_URL')
        if url is None:
            return self.assertEqual(True, True)
        crawler = Crawler()
        cache = crawler.get_cache(url, 'hv', 'hive', NAME)
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None

    def test_kafka(self):
        url = ENV('TEST_KAFKA_CONNECTION_URL')
        if url is None:
            return self.assertEqual(True, True)

        crawler = Crawler()
        crawler.generate_topic_info('guoshuLogUserlogininfo', url)
        cache = crawler.get_cache(url, 'kf', 'kafka', NAME)
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None


if __name__ == '__main__':
    unittest.main()
