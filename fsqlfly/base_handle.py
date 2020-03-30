# -*- coding:utf-8 -*-
import json
from typing import Any
from abc import ABC
import tornado
import tornado.web


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
        return self.get_cookie('user')

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

        # Set up response dictionary.
        self.response = dict()

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

        self.response = kwargs
        self.write_json()

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)
        self.finish()
