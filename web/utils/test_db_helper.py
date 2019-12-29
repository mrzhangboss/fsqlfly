import unittest
from utils.db_crawler import Crawler
from utils.db_helper import DBProxy
from web.settings import ENV
from utils.strings import clean_sql, build_select_sql, parse_sql, SqlProps

NAME = 'TEST'


class MyTestCase(unittest.TestCase):
    def test_get_mysql_table(self):
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
        data = proxy.get_table(source_tb, search=f" $username = '{django_admin}' /* mode= xx */", table_name=search_tb,
                               limit=100)
        self.assertEqual(data.tableName, search_tb)

    def test_get_hive_table(self):
        db_name = ENV('TEST_HIVE_DB_NAME')
        table_name = ENV('TEST_HIVE_TABLE_NAME')
        table_search = ENV('TEST_HIVE_TABLE_SEARCH')
        hive_url = ENV('TEST_HIVE_CONNECTION_URL')
        suffix = '_hv'
        cache = Crawler().get_cache(hive_url, suffix, 'hive', NAME)
        proxy = DBProxy([cache])

        data = proxy.get_table(table_name, search=table_search, table_name=table_name,
                               limit=100)
        self.assertEqual(data.tableName, table_name)

    def test_get_kafka_table(self):
        url = ENV('TEST_KAFKA_CONNECTION_URL')
        suffix = 'kafka'
        cache = Crawler().get_cache(url, suffix, 'kafka', NAME)
        proxy = DBProxy([cache])
        table_name = ENV('TEST_KAFKA_TABLE_NAME')
        table_search = ENV('TEST_KAFKA_TABLE_SEARCH')

        data = proxy.get_table(table_name, search=table_search, table_name=table_name,
                               limit=100)

    def test_sql_function(self):
        for sql, res in [
            ('xxx /* xdsf */', [SqlProps('xdsf', True)]),
            ('xxx /* xdsf= */', [SqlProps('xdsf', '')]),
            ('xxx /* xdsf=a */', [SqlProps('xdsf', 'a')]),
            ('xxx /* xdsf=\' xxx\' */', [SqlProps('xdsf', ' xxx')]),
            ('xxx /* xdsf=" xxx" */', [SqlProps('xdsf', ' xxx')]),
            ('xxx /* xdsf= 1 */', [SqlProps('xdsf', 1)]),
            ('xxx /* xdsf= 1.0 */', [SqlProps('xdsf', 1)]),
            ('xxx /* xdsf xdsf= 1.0 */', [SqlProps('xdsf xdsf', 1)]),
        ]:
            self.assertTrue(clean_sql(sql) == 'xxx')
            for p, r_p in zip(parse_sql(sql), res):
                self.assertEqual(p, r_p)

    def test_build_sql(self):
        header = 'select * from '
        for params, out in [
            (('$id = 1 /* mode = latest */', 'ab'), header + 'ab where ab.id = 1'),
            (('$id = 1 /* mode = latest */', 'ab', 10), header + 'ab where ab.id = 1 limit 10'),
            (('$id = 1 /* mode = latest */', 'ab', 100, 10), header + 'ab where ab.id = 1 limit 10, 100'),
            (('$id = 1 ;drop table ab;select * from ab where 1 = 1', 'ab', 100, 10), Exception("xx")),
        ]:
            if isinstance(out, Exception):
                self.assertRaises(Exception, build_select_sql, *params)
            else:
                self.assertEqual(build_select_sql(*params), out)


if __name__ == '__main__':
    unittest.main()
