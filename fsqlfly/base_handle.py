# -*- coding:utf-8 -*-
import json
import logging
from typing import Any
from abc import ABC
import tornado
import tornado.web
from fsqlfly import settings


class RespCode:
    Success = 200
    NeedLogin = 500
    LoginFail = 501
    InvalidHttpMethod = 405


class BaseHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""

    @property
    def terminal_manager(self):
        return self.settings['terminal_manager']

    def get_current_user(self) -> Any:
        cookie = self.get_cookie('user')
        if cookie:
            return True
        token = self.request.arguments.get('token')
        if len(token) == 0:
            token = self.request.headers.get('token')
        logging.debug("Try Login By token {}".format(token))

        if len(token) == 1 and token[0] == settings.FSQLFLY_TOKEN_BYTE:
            logging.debug("Login By token {}".format(token))
            return True
        return False

    def get_login_url(self) -> str:
        return '/login'

    def set_login_status(self):
        self.set_cookie('user', 'admin')

    def prepare(self):
        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError:
                msg = 'Unable to parse JSON.'
                self.send_error(400, msg=msg)  # Bad Request

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    code_msg = {
        RespCode.NeedLogin: 'Need Login',
        RespCode.LoginFail: 'Wrong Password or Token',
        RespCode.InvalidHttpMethod: 'Invalid HTTP method.'
    }

    def write_error(self, status_code, **kwargs):
        kwargs['code'] = status_code
        if 'msg' not in kwargs:
            kwargs['msg'] = self.code_msg.get(status_code, 'Unknown error.')

        self.write_json(kwargs)

    def write_json(self, res):
        output = json.dumps(res)
        self.write(output)
        self.finish()
