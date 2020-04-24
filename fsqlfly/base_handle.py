# -*- coding:utf-8 -*-
import json
import attr
from logzero import logger
from typing import Any, Optional, Awaitable
from datetime import datetime, date
from tornado.web import RequestHandler
from fsqlfly import settings
from fsqlfly.common import DBRes
from fsqlfly.utils.strings import dict2camel, dict2underline


def json_obj_hook(o):
    if isinstance(o, (date, datetime)):
        return str(o)


class BaseHandler(RequestHandler):
    """Request handler where requests and responses speak JSON."""

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        return super(BaseHandler, self).data_received(chunk)

    @property
    def terminal_manager(self):
        return self.settings['terminal_manager']

    def _login_by_header(self):
        token = self.request.headers.get('Token')
        if token is not None:
            logger.debug("try login by request header {}".format(token))
            if token == settings.FSQLFLY_TOKEN:
                logger.debug("login success by request header {}".format(token))
                return token
        return None

    def get_current_user(self) -> Any:
        cookie = self.get_cookie('user')
        if cookie:
            return cookie
        header_token = self._login_by_header()
        if header_token:
            return header_token
        token = self.request.arguments.get('token')
        if token is not None and len(token) == 1 and token[0] == settings.FSQLFLY_TOKEN_BYTE:
            logger.debug("login success By token {}".format(token))
            return token

    def get_login_url(self) -> str:
        return '/login'

    def set_login_status(self):
        self.set_secure_cookie('user', 'admin')

    def set_logout_status(self):
        self.clear_cookie('user')

    @property
    def json_body(self) -> dict:
        _name = '_save_json_data'
        if not hasattr(self, _name):
            try:
                json_data = json.loads(self.request.body)
                if isinstance(json_data, dict):
                    json_data = dict2underline(json_data)
                setattr(self, _name, json_data)
            except ValueError:
                setattr(self, _name, {})

        return getattr(self, _name)

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    def write_json(self, res: dict):
        output = json.dumps(res, ensure_ascii=False, default=json_obj_hook)
        self.write(output)
        self.finish()

    def write_res(self, res: DBRes):
        data = attr.asdict(res)
        j_data = json.dumps(dict2camel(data), ensure_ascii=False, default=json_obj_hook)
        self.write(j_data)
        self.finish()
