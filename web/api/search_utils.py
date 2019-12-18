# -*- coding:utf-8 -*-
from typing import Callable, Optional, Union
from datetime import datetime, date, timedelta, time

BASIC_GLOBAL = {'datetime': datetime, 'date': date, 'timedelta': timedelta, 'time': time,
                'now': datetime.now(), 'today': date.today()}


def build_function(code: str, suffix='$', out_put_function_name='__generate_function__') -> Union[Callable[[object], bool], Exception]:
    out_put_scope = dict()
    real_function = '{} = lambda x: {}'.format(out_put_function_name, code.replace(suffix, 'x.'))
    try:
        exec(real_function, BASIC_GLOBAL, out_put_scope)
        return out_put_scope[out_put_function_name]
    except Exception as e:
        print(e)
        print(real_function)
        return e
