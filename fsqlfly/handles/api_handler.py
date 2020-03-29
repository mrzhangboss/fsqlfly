# -*- coding:utf-8 -*-
import tornado
import tornado.web
import json
from typing import Optional, Awaitable

from fsqlfly.handles.base_handle import BaseHandler, RespCode
from fsqlfly import settings

is_login = False
user = dict(code=200, name='flink', status='ok', currentAuthority='admin', type='password',
            avatar='https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png')


class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user is None:
            self.write_error(500)
        else:
            self.response = user
            self.write_json()

    def post(self):
        print(self.request.arguments)
        arg = self.request.arguments
        if (arg.get('type') == 'account' and arg.get('password') == settings.FSQLFLY_PASSWORD) or (
                arg.get('type') == 'token' and arg.get('token') == settings.FSQLFLY_TOKEN
        ):
            self.set_login_status()
            self.response = user
            self.write_json()
        else:
            self.write_error(RespCode.LoginFail)


default_handlers = [(r'/api/login', LoginHandler)]
