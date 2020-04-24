import tornado.web
from terminado import TermSocket
from fsqlfly.common import safe_authenticated
from fsqlfly import settings
from fsqlfly.base_handle import BaseHandler
from fsqlfly.workflow import run_debug_transform
from fsqlfly.common import DBRes
from fsqlfly.utils.job_manage import handle_job
from fsqlfly.db_helper import DBDao


class TerminalHandler(BaseHandler):
    @safe_authenticated
    def get(self):
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_res(DBRes(data=terms))


class TransformControlHandler(BaseHandler):
    @safe_authenticated
    def post(self, mode: str, pk: str):
        if mode == 'debug':
            term = run_debug_transform(self.json_body, self.terminal_manager)
            self.write_res(DBRes({"url": '/terminal/{}'.format(term)}))
        else:
            if not pk.isdigit():
                transform = DBDao.get_transform(pk=pk)
                pk = str(transform.id)
            return self.write_res(handle_job(mode, pk, self.json_body))


class TerminalStopHandler(BaseHandler):
    @safe_authenticated
    async def post(self, name: str):
        tm = self.terminal_manager
        if name in tm.terminals:
            await tm.terminate(name, force=True)
            self.write_res(DBRes())
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
