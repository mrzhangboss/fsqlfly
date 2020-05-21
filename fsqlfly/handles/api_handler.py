# -*- coding:utf-8 -*-
from typing import Optional
from fsqlfly.base_handle import BaseHandler
from fsqlfly import settings
from fsqlfly.common import DBRes

is_login = False
user = dict(code=200, name='admin', status='ok', currentAuthority='admin', type='password',
            token=settings.FSQLFLY_TOKEN, success=True, deletable=settings.FSQLFLY_SAVE_MODE_DISABLE)


class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user is None:
            self.write_error(500)
        else:
            self.write_json(user)

    @classmethod
    def is_login(cls, login_type: str, password: Optional[str], token: Optional[str]):
        if login_type == 'account':
            return password == settings.FSQLFLY_PASSWORD
        if login_type == 'token':
            return token == settings.FSQLFLY_TOKEN
        return False

    def post(self):
        arg = self.json_body
        if self.is_login(arg.get('type'), arg.get('password'), arg.get('type')):
            self.set_login_status()
            self.write_json(user)
        else:
            self.write_res(DBRes.login_error())


class LoginOutHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.set_logout_status()
            self.write_json(user)


default_handlers = [
    (r'/api/login', LoginHandler),
    (r'/api/logout', LoginOutHandler),
]
