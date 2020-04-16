import sys
import re
import argparse
from typing import Optional, List
import os
import re
import time
import sys
from typing import List, Dict, Optional
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.engine import reflection
from collections import namedtuple


class BaseHelper(object):
    @classmethod
    def run(cls, commands: list):
        raise NotImplementedError("Need Implement")


def generate_hive_create(self, args):
    pass


def generate_partition_name(pt_name):
    return f"""PARTITIONED BY (
         {pt_name} STRING COMMENT '分区字段'
    )"""


def create_hive_table(name: str, columns: List[dict], table_comment: Optional[str],
                      output, hive_database, partition, pt_name):
    print(f'use {hive_database};', file=output)
    print(f'CREATE TABLE IF NOT EXISTS `{name}` (', file=output)
    is_first = True
    for col in columns:
        print(('' if is_first else ',\n') + " " * 4, end='', file=output)
        if is_first:
            is_first = False

        # print(col['type'], type(col['type']))
        _t = col['type']
        _n = col['name']
        _c = col['comment']
        t_name = str(_t)
        simple = re.findall(r"(\w+\(\d+,?\s*\d*\))\s*", t_name)
        if simple:
            r_name = simple[0]
        else:
            r_name = t_name.split(' ')[0]

        if r_name.startswith('BIGINT') or r_name.startswith('INTEGER'):
            r_name = r_name.split('(')[0]

        if r_name.startswith('SMALLINT'):
            r_name = 'INT'

        if t_name.endswith('TEXT') or t_name.startswith('VARBINARY'):
            r_name = "STRING"

        if t_name.startswith('DATETIME'):
            r_name = 'TIMESTAMP'

        comment = f" COMMENT '{_c}'" if _c else ''
        column = f'`{_n}` {r_name}{comment}'
        print(column, file=output, end='')
    print('\n)', file=output)
    if table_comment:
        print(f'COMMENT "{table_comment}"', file=output)
    if partition:
        print(generate_partition_name(pt_name), file=output)
    print(';', file=output)


def dump_db2hive(name: str, columns: List[dict],
                 output, hive_database, partition, pt_name):
    pass


class DBToHive(BaseHelper):
    @classmethod
    def run(cls, commands: list):
        parser = argparse.ArgumentParser(description='Generate daily backup data from database To Hive SQL')
        parser.add_argument('--database', help='database name')
        parser.add_argument('--host', help='database host')
        parser.add_argument('--user', help='database user')
        parser.add_argument('--password', help='database user password', default=None)
        parser.add_argument('--table', help='backup table name', default='*')
        parser.add_argument('--port', help='database port', type=int, default=3306)
        parser.add_argument('--output', help='output file name if null then print', default=None)
        parser.add_argument('--hive_database', help='dump hive database if null then the db database name',
                            default=None)
        parser.add_argument('--hive_catalog', help='hive catalog setting in your flink sql config',
                            default='myhive')
        parser.add_argument('--partition', help='add partition table', action='store_true', default=False)
        parser.add_argument('--pt_name', help='partition name', default='pt')
        parser.add_argument('--db_type', help='database type', default='mysql', choices=['mysql', 'postgresql'])

        args = parser.parse_args(commands)
        if args.password is None:
            password = input('your database base password:')
            args.__setattr__('password', password.strip())
        if args.output is None:
            args.__setattr__('output', sys.stdout)
        else:
            args.__setattr__('output', open(args.output, 'w'))

        if args.hive_database is None:
            args.__setattr__('hive_database', args.database)
        driver = 'pymysql' if args.db_type == 'mysql' else 'psycopg2'
        db_url = f"{args.db_type}+{driver}://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}?charset=utf8"

        engine = create_engine(db_url)
        insp = inspect(engine)
        all_tables_names = insp.get_table_names()
        tables = all_tables_names if args.table == '*' else args.table.split(',')

        need_tables = set()

        for x in tables:
            if x not in all_tables_names:
                print('table {} not found in database'.format(x))

        for n in need_tables:
            t_comment = insp.get_table_comment(n)['text']
            cs = insp.get_columns(n)
            create_hive_table(n, columns=cs, table_comment=t_comment, output=args.output,
                              hive_database=args.hive_database, partition=args.partition, pt_name=args.pt_name)

        for n in need_tables:
            cs = insp.get_columns(n)
            dump_db2hive(n, columns=cs, output=args.output,
                         hive_database=args.hive_database, partition=args.partition, pt_name=args.pt_name)

        # print(args)


if __name__ == '__main__':
    DBToHive.run(['--database', 'data', '--host', 'localhost', '--user', 'root', '--partition', '--password', 'abc',
                  '--hive_database', 'example'])
