# -*- coding:utf-8 -*-
import json
import logging
from typing import Any
from abc import ABC
from datetime import datetime, date
import tornado
import tornado.web
from fsqlfly import settings


class RespCode:
    Success = 200
    NeedLogin = 500
    LoginFail = 501
    APIFail = 502
    InvalidHttpMethod = 405


def json_obj_hook(o):
    if isinstance(o, (date, datetime)):
        return str(o)


class BaseHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""

    @property
    def terminal_manager(self):
        return self.settings['terminal_manager']

    def get_current_user(self) -> Any:
        cookie = self.get_cookie('user')
        if cookie:
            return cookie
        token = self.request.arguments.get('token')
        if token is None:
            token = self.request.headers.get('token')
        logging.debug("Try Login By token {}".format(token))

        if token is not None and len(token) == 1 and token[0] == settings.FSQLFLY_TOKEN_BYTE:
            logging.debug("Login By token {}".format(token))
            return token
        return None

    def get_login_url(self) -> str:
        return '/login'

    def set_login_status(self):
        self.set_cookie('user', 'admin')

    @property
    def json_body(self) -> dict:
        _name = '_save_json_data'
        if not hasattr(self, _name):
            try:
                json_data = json.loads(self.request.body)
                setattr(self, _name, json_data)
            except ValueError:
                setattr(self, _name, {})

        return getattr(self, _name)

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    code_msg = {
        RespCode.NeedLogin: 'Need Login',
        RespCode.LoginFail: 'Wrong Password or Token',
        RespCode.InvalidHttpMethod: 'Invalid HTTP method.',
        RespCode.APIFail: 'Invalid API Request',
    }

    def write_error(self, status_code, **kwargs):
        kwargs['code'] = status_code
        if 'msg' not in kwargs:
            kwargs['msg'] = self.code_msg.get(status_code, 'Unknown error.')

        self.write_json(kwargs)

    def write_json(self, res: dict):
        output = json.dumps(res, ensure_ascii=False, default=json_obj_hook)
        self.write(output)
        self.finish()
