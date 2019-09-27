# -*- coding: utf-8 -*-
from typing import Optional, Union
from django.http import JsonResponse

from utils.strings import dict2camel


def create_response(data: Union[Optional[dict], list] = None, code: int = 0, msg: str = '') -> JsonResponse:
    return JsonResponse(dict2camel({'data': data, 'code': code, 'success': code == 0, 'msg': msg}))
