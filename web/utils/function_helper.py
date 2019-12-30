# -*- coding:utf-8 -*-
from typing import Callable, Optional, Union
from datetime import datetime, date, timedelta, time


class FakeNoneObject:
    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False


FAKE_NONE = FakeNoneObject()


class Dict2Obj:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def __getattr__(self, item):
        return FAKE_NONE


BASIC_GLOBAL = {'datetime': datetime, 'date': date, 'timedelta': timedelta, 'time': time,
                'now': datetime.now(), 'today': date.today()}


def build_function(code: str, suffix='$', out_put_function_name='__generate_function__') -> Union[
    Callable[[object], bool], Exception]:
    out_put_scope = dict()
    real_function = '{} = lambda x: {}'.format(out_put_function_name, code.replace(suffix, 'x.'))
    try:
        exec(real_function, BASIC_GLOBAL, out_put_scope)
        return out_put_scope[out_put_function_name]
    except Exception as e:
        print(e)
        print(real_function)
        return e
