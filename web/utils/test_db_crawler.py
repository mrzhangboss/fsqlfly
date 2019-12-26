import attr
import pickle
import json
from utils.db_crawler import Crawler
from pprint import pprint
from web.settings import ENV
import unittest


class MyTestCase(unittest.TestCase):

    def test_mysql(self):
        url = ENV('TEST_MYSQL_CONNECTION_URL')
        if url is None:
            return self.assertEqual(True, True)
        crawler = Crawler()
        cache = crawler.get_cache(url, 'ms', 'mysql')
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None

    def test_hive(self):
        url = ENV('TEST_HIVE_CONNECTION_URL')
        if url is None:
            return self.assertEqual(True, True)
        crawler = Crawler()
        cache = crawler.get_cache(url, 'hv', 'hive')
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None

    def test_kafka(self):
        url = ENV('TEST_KAFKA_CONNECTION_URL')
        if url is None:
            return self.assertEqual(True, True)

        crawler = Crawler()
        crawler.generate_topic_info('guoshuLogUserlogininfo',  url)
        cache = crawler.get_cache(url, 'kf', 'kafka')
        pprint(attr.asdict(cache))
        data = pickle.dumps(cache)
        assert data is not None


if __name__ == '__main__':
    unittest.main()
