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
    data: Any = attr.ib(default=None)
    code: int = attr.ib(default=200)
    msg: Optional[str] = attr.ib(default=None)
    success: bool = attr.ib()

    @success.default
    def get_success(self):
        return self.code == 200

    @classmethod
    def api_error(cls, msg: str = RespCode.APIFail.msg):
        return DBRes(code=RespCode.APIFail.code, msg=msg)

    @classmethod
    def not_found(cls, msg: str = "Can't found Object"):
        return DBRes(code=RespCode.APIFail.code, msg=msg)

    @classmethod
    def resource_locked(cls, msg: str = "Resource Locked"):
        return DBRes(code=RespCode.APIFail.code, msg=msg)

    @classmethod
    def sever_error(cls, msg: str = RespCode.ServerError.msg):
        return DBRes(code=RespCode.ServerError.code, msg=msg)
