import json
import tornado.web
from terminado import TermSocket
from tornado.web import authenticated
from fsqlfly import settings
from fsqlfly.base_handle import BaseHandler
from fsqlfly.workflow import run_debug_transform
from fsqlfly.utils.response import create_response


class TerminalHandler(BaseHandler):
    @authenticated
    def get(self):
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_json(dict(data=terms))


class TerminalNewHandler(BaseHandler):
    @authenticated
    def get(self):
        pass

    @authenticated
    def post(self, *args, **kwargs):
        num = run_debug_transform(self.request.arguments, self.terminal_manager)
        self.write_json(create_response({"url": '/terminal/{}'.format(num)}))


class TerminalStopHandler(BaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        print(args)
        self.write_json(create_response())


default_handlers = [
    (r'/api/terminal', TerminalHandler),
    (r"/_websocket/(\w+)", TermSocket, {'term_manager': settings.TERMINAL_MANAGER}),
    (r'/api/transform/debug/(\d+)', TerminalNewHandler),
    (r'/api/terminal/stop/(\d+)', TerminalStopHandler),
]
