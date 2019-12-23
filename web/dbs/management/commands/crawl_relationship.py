# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects.mysql.types import (_StringType, _FloatType, _IntegerType, DECIMAL, DATETIME, TIMESTAMP, BIT,
                                             TIME,
                                             BIGINT)
from dbs.management.commands.load_mysql_resource import Category

class Command(BaseCommand):
    help = 'Canal Consumer'

    def add_arguments(self, parser):
        parser.add_argument('--host', action='store', help='mysql host')
        parser.add_argument('--database', action='store', help='mysql database')
        parser.add_argument('--namespace', action='store', help='basic namespace')
        parser.add_argument('--category', action='store', help='from system', default="mysql",
                            choices=['mysql', 'es', 'kafka'])
        parser.add_argument('--tables', action='store', help='mysql tables', default="*")
        parser.add_argument('--kafka-bootstrap', action='store', help='kafka bootstrap servers',
                            default="localhost:9092", dest='kafka')
        parser.add_argument('--es-hosts', action='store', help='elastic search host port,sepe by ,',
                            default="http://localhost:9200", dest='es')
        parser.add_argument('--port', action='store', help='mysql port', default=3306, type=int)
        parser.add_argument('--password', action='store', help='mysql password, if not set must input when running',
                            default=None)
        parser.add_argument('--username', action='store', help='mysql username', default='root')


    def handle(self, *args, **options):
        if options['password'] is None:
            self.stdout.write(self.style.WARNING("you not set mysql password please input in command line!!!"))
            password = input("Your MySQL Password:")
            options['password'] = password
        else:
            password = options['password']


        category = options['category']
        full_namespace = '' + '_' + category

        username, host, port, database = options['username'], options['host'], options['port'], options['database']
        db_url = f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}?charset=utf8"

        engine = create_engine(db_url)
        insp = inspect(engine)
        tables_str = options['tables']
        table_names = set(insp.get_table_names())
        if tables_str == '*':
            need_tables = set(table_names)
        else:
            need_tables = set(tables_str.strip().split(','))

        for n in table_names:
            if n not in need_tables:
                continue
            t_comment = insp.get_table_comment(n)['text']
            cs = insp.get_columns(n)
            foreign_keys = insp.get_foreign_keys(n)
            unique_keys = insp.get_unique_constraints(n)
            for key in foreign_keys:
                assert len(key['referred_columns']) == 1
                assert len(key['constrained_columns']) == 1
                print(key['referred_table'], print(key['referred_columns'][0]))
                print(n, print(key['constrained_columns'][0]))
        table_nums = len(need_tables)
        self.stdout.write(self.style.SUCCESS(f'Successfully load {table_nums} table from {database}: {tables_str}'))
