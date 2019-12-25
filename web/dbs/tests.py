from django.test import TestCase
from web.settings import ENV
from dbs.models import Connection, Relationship, ConnectionType
from utils.db_crawler import Crawler


# Create your tests here.
class ConnectionTestCase(TestCase):
    def setUp(self) -> None:
        self.test_mysql_url = ENV('TEST_MYSQL_CONNECTION_URL')
        if self.test_mysql_url is None:
            return
        self.mysql_connection = Connection.objects.create(name='test_mysql', typ=ConnectionType.MYSQL.name)

    def test_get_cache_from_mysql(self):
        if self.test_mysql_url is None:
            return
        con = self.mysql_connection
        crawler = Crawler(con.url, ConnectionType.MYSQL.suffix, con.typ)
        crawler.get_cache()


class RelationshipTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_build_cache_from_config(self):
        pass
