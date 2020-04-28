# -*- coding:utf-8 -*-
import functools
import urllib
import traceback
import attr
from urllib.parse import urlencode
from typing import Any, Optional, NamedTuple, Callable, Awaitable, Union
from tornado.web import RequestHandler, HTTPError
from logzero import logger

SUPPORT_TABLE_TYPE = {'sink', 'source', 'both', 'view', 'temporal-table'}
SUPPORT_MANAGER = {'hive', 'db', 'kafka', 'hbase', 'elasticsearch', 'canal', 'file'}


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
    def login_error(cls, msg: str = RespCode.LoginFail.code):
        return DBRes(code=RespCode.LoginFail.code, msg=msg)

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


def safe_authenticated(
        method: Callable[..., Optional[Awaitable[None]]]
) -> Callable[..., Union[Optional[Awaitable[None]], DBRes]]:
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """

    @functools.wraps(method)
    def wrapper(  # type: ignore
            self: RequestHandler, *args, **kwargs
    ) -> Union[Optional[Awaitable[None]], DBRes]:
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urllib.parse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        assert self.request.uri is not None
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return None
            raise HTTPError(403)
        try:
            return method(self, *args, **kwargs)
        except Exception as error:
            from fsqlfly import settings
            if settings.FSQLFLY_DEBUG:
                raise error
            err = traceback.format_exc()
            logger.error(err)
            return DBRes.sever_error(msg=f'meet {err}')

    return wrapper
