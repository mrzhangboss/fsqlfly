"""One shared terminal per URL endpoint

Plus a /new URL which will create a new terminal and redirect to it.
"""
from __future__ import print_function, absolute_import
import logging
import os.path
import sys
from base64 import b64decode, b64encode
import tornado.web
# This demo requires tornado_xstatic and XStatic-term.js
import tornado_xstatic

from terminado import TermSocket, NamedTermManager
from common_demo_stuff import run_and_show_browser, STATIC_DIR, TEMPLATE_DIR

AUTH_TYPES = ("none", "login")


class TerminalPageHandler(tornado.web.RequestHandler):
    """Render the /ttyX pages"""

    def get(self, term_name):
        return self.render("termpage.html", static=self.static_url,
                           xstatic=self.application.settings['xstatic_url'],
                           ws_url_path="/_websocket/" + term_name)


class NewTerminalHandler(tornado.web.RequestHandler):
    """Redirect to an unused terminal name"""



    def get(self):
        command = self.get_query_argument('command', None)
        command_file = self.get_query_argument('filename', None)
        manager = self.application.settings['term_manager']
        name = manager._next_available_name()
        terminal_commands = dict()
        if command:
            shell_command = b64decode(command).decode()
            real_command = shell_command.format('__TEMPORARY__' + name).split()
            print(real_command)
            terminal_commands['shell_command'] = real_command


        term = manager.new_terminal(**terminal_commands)

        if command_file:
            lines = open(command_file).read()
            print(lines)
            term.ptyproc.write(lines)
        manager.log.info("New terminal with automatic name: %s", name)
        term.term_name = name
        manager.terminals[name] = term
        manager.start_reading(term)

        self.redirect("/" + name, permanent=False)


def main():
    term_manager = NamedTermManager(shell_command=['bash', '/opt/flink-1.9.0/bin/sql-client.sh'],
                                    max_terminals=100)

    handlers = [
        (r"/_websocket/(\w+)", TermSocket,
         {'term_manager': term_manager}),
        (r"/new/?", NewTerminalHandler),
        (r"/(\w+)/?", TerminalPageHandler),
        (r"/xstatic/(.*)", tornado_xstatic.XStaticFileHandler)
    ]
    application = tornado.web.Application(handlers, static_path=STATIC_DIR,
                                          template_path=TEMPLATE_DIR,
                                          xstatic_url=tornado_xstatic.url_maker('/xstatic/'),
                                          term_manager=term_manager)

    application.listen(8700, 'localhost')
    command = b64encode(b'bash /opt/flink-1.9.0/bin/sql-client.sh embedded -s {}').decode()
    run_and_show_browser("http://localhost:8700/new/?command=" + command, term_manager)


if __name__ == "__main__":
    main()
