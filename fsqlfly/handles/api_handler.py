# -*- coding:utf-8 -*-

from fsqlfly.base_handle import BaseHandler, RespCode
from fsqlfly import settings

is_login = False
user = dict(code=200, name='flink', status='ok', currentAuthority='admin', type='password',
            avatar='https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png',
            token=settings.FSQLFLY_TOKEN)


class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user is None:
            self.write_error(500)
        else:
            self.write_json(user)

    def post(self):
        print(self.request.arguments)
        arg = self.json_body
        if (arg.get('type') == 'account' and arg.get('password') == settings.FSQLFLY_PASSWORD) or (
                arg.get('type') == 'token' and arg.get('token') == settings.FSQLFLY_TOKEN
        ):
            self.set_login_status()
            self.write_json(user)
        else:
            self.write_error(RespCode.LoginFail)


default_handlers = [(r'/api/login', LoginHandler)]
