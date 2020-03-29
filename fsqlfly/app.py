# -*- coding:utf-8 -*-
import os
import tornado.ioloop
import tornado.web
from fsqlfly import settings
from fsqlfly import handles


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_header('content-type', 'text/html')
        self.write(settings.INDEX_HTML)


if __name__ == "__main__":
    application = tornado.web.Application(
        handles.all_handles + [
            (r"/static/(.*)", tornado.web.StaticFileHandler,
             {"path": settings.FSQLFLY_STATIC_ROOT}),
            (r"/(.*)", IndexHandler),
        ],
        cookie_secret=settings.FSQLFLY_COOKIE_SECRET,
        login_url='/login',
        debug=True
    )
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()
