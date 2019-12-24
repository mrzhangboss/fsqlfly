# -*- coding:utf-8 -*-
from sqlalchemy import create_engine, inspect


class Crawler:
    def __init__(self, connection_url: str, suffix: str, typ: str):
        self.url = connection_url
        self.suffix = suffix
        self.typ = typ

    def get_cache(self):
        engine = create_engine(self.url)
        insp = inspect(engine)

        table_names = set(insp.get_table_names())
        for n in table_names:
            t_comment = insp.get_table_comment(n)['text']
            cs = insp.get_columns(n)
            foreign_keys = insp.get_foreign_keys(n)
            unique_keys = insp.get_unique_constraints(n)
            for key in foreign_keys:
                assert len(key['referred_columns']) == 1
                assert len(key['constrained_columns']) == 1
                print(key['referred_table'], print(key['referred_columns'][0]))
                print(n, print(key['constrained_columns'][0]))
