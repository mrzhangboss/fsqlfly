import asyncio
import time
import tornado.web
from terminado import TermSocket
from tornado.web import authenticated
from fsqlfly import settings
from fsqlfly.base_handle import BaseHandler, RespCode
from fsqlfly.workflow import run_debug_transform
from fsqlfly.utils.response import create_response
from fsqlfly.models import Transform
from fsqlfly.utils.job_manage import handle_job


class TerminalHandler(BaseHandler):
    @authenticated
    def get(self):
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_json(create_response(data=terms))


class TransformControlHandler(BaseHandler):
    @authenticated
    def post(self, mode: str, pk: str):
        if mode == 'debug':
            term = run_debug_transform(self.json_body, self.terminal_manager)
            self.write_json(create_response({"url": '/terminal/{}'.format(term)}))
        else:
            if not pk.isdigit():
                transform = Transform.select().filter(Transform.name == pk).get()
                pk = str(transform.id)
            return self.write_json(handle_job(mode, pk, self.json_body))


class TerminalStopHandler(BaseHandler):
    @authenticated
    async def post(self, name: str):
        tm = self.terminal_manager
        if name in tm.terminals:
            await tm.terminate(name, force=True)
            self.write_json(create_response())
        else:
            raise tornado.web.HTTPError(404, "Terminal not found: %r" % name)


class MyTermSocket(TermSocket):
    def open(self, url_component=None):
        super(MyTermSocket, self).open(url_component)
        terminal = self.term_manager.get_terminal(url_component)
        open_name = settings.TERMINAL_OPEN_NAME
        if hasattr(terminal, open_name) and getattr(terminal, open_name):
            setattr(terminal, open_name, False)
            self.term_manager.start_reading(terminal)


default_handlers = [
    (r'/api/terminal', TerminalHandler),
    (r"/_websocket/(\w+)", MyTermSocket, {'term_manager': settings.TERMINAL_MANAGER}),
    (r'/api/terminal/stop/(?P<name>\d+)', TerminalStopHandler),
    (r'/api/transform/(\w+)/([0-9a-zA-Z_]+)', TransformControlHandler),
]
