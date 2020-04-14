# -*- coding: utf-8 -*-
from typing import Optional, Union

from fsqlfly.utils.strings import dict2camel


def create_response(data: Union[Optional[dict], list] = None, code: int = 200, msg: str = '') -> dict:
    return dict2camel({'data': data, 'code': code, 'success': code == 200, 'msg': msg})
