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


class TerminalHandler(BaseHandler):
    @authenticated
    def get(self):
        tm = self.terminal_manager
        terms = [{'name': name, 'id': name} for name in tm.terminals]
        self.write_json(create_response(data=terms))


class TerminalNewHandler(BaseHandler):
    @classmethod
    async def test_term_alive(cls, term, max_s=2):
        start = time.time()
        msgs = ['running commands: \n', term.run_command, '\nerror info\n']
        while time.time() - start < max_s:
            if not term.ptyproc.isalive():
                return ''.join(msgs)
            msgs.append(term.ptyproc.read())
            await asyncio.sleep(.5)
        return ''.join(msgs)




    @authenticated
    async def post(self, mode: str, pk: int):
        if mode == 'debug':
            term = run_debug_transform(self.json_body, self.terminal_manager)
            msg = await self.test_term_alive(term)
            if term.ptyproc.isalive():
                self.write_json(create_response({"url": '/terminal/{}'.format(term.term_name)}))
            else:
                # self.write_error(RespCode.APIFail, msg=term.ptyproc.read())
                self.write_error(RespCode.APIFail, msg=msg)


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
