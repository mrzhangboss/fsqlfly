import tornado.web
from terminado import TermSocket
from tornado.web import authenticated
from fsqlfly import settings
from fsqlfly.base_handle import BaseHandler, RespCode
from fsqlfly.workflow import run_debug_transform
from fsqlfly.utils.response import create_response
from fsqlfly.models import Transform


class TerminalHandler(BaseHandler):
    @authenticated
    def get(self):
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_json(dict(data=terms))


class TerminalNewHandler(BaseHandler):
    @authenticated
    def post(self, mode: str, pk: int):
        if mode == 'debug':
            num = run_debug_transform(self.json_body, self.terminal_manager)
            self.write_json(create_response({"url": '/terminal/{}'.format(num)}))
        else:
            self.redirect('/api/job/{}/{}'.format(mode, pk))


class TerminalStopHandler(BaseHandler):
    @authenticated
    async def post(self, name: str):
        tm = self.terminal_manager
        if name in tm.terminals:
            await tm.terminate(name, force=True)
            self.write_json(create_response())
        else:
            raise tornado.web.HTTPError(404, "Terminal not found: %r" % name)


default_handlers = [
    (r'/api/terminal', TerminalHandler),
    (r"/_websocket/(\w+)", TermSocket, {'term_manager': settings.TERMINAL_MANAGER}),
    (r'/api/terminal/stop/(?P<name>\d+)', TerminalStopHandler),
    (r'/api/transform/(\w+)/(\d+)', TerminalNewHandler),
]
