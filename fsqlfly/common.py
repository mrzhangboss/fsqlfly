# -*- coding:utf-8 -*-
import attr
from typing import Any, Optional, NamedTuple
from collections import namedtuple


class CodeMsg(NamedTuple):
    code: int
    msg: str


class RespCode:
    Success = CodeMsg(200, 'Success')
    ServerError = CodeMsg(500, 'Web Server Error')
    NeedLogin = CodeMsg(503, 'You Need Login')
    LoginFail = CodeMsg(501, 'Wrong Password or Token')
    APIFail = CodeMsg(502, 'Invalid API Request')
    InvalidHttpMethod = CodeMsg(405, 'Invalid HTTP method.')


@attr.s
class DBRes:
    data: Any = attr.ib()
    code: int = attr.ib(default=200)
    msg: Optional[str] = attr.ib(default=None)
    success: bool = attr.ib(default=True)
