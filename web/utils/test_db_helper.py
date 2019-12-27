import unittest
from utils.db_crawler import Crawler
from utils.db_helper import DBProxy
from web.settings import ENV

NAME = 'TEST'


class MyTestCase(unittest.TestCase):
    def test_get_table(self):
        db_name = ENV('DB_NAME')
        django_url = 'mysql://{user}:{password}@{host}:{port}/{db_name}'.format(
            db_name=db_name,
            host=ENV('DB_HOST'),
            user=ENV('DB_USER'),
            password=ENV('DB_PASSWORD'),
            port=ENV('DB_PORT', 3306))
        suffix = '_my'
        cache = Crawler().get_cache(django_url, suffix, 'mysql', NAME)
        proxy = DBProxy([cache])


        def gen_real_db_name(tb_name: str) -> str:
            return db_name + suffix + '.' + tb_name

        django_admin = ENV('TEST_DJANGO_USER_NAME', 'admin')
        source_tb = gen_real_db_name('auth_user')
        search_tb = gen_real_db_name('django_admin_log')
        data = proxy.get_table(source_tb, search=f" $username = '{django_admin}' ", table_name=search_tb, limit=100)
        self.assertTrue(len(data) > 1)


if __name__ == '__main__':
    unittest.main()
