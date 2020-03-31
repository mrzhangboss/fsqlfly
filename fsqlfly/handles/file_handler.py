# -*- coding:utf-8 -*-
import os
import magic
from tempfile import mkstemp
import tornado.web
from tornado.web import authenticated
from fsqlfly.base_handle import BaseHandler, RespCode
from fsqlfly.utils.response import create_response
from fsqlfly import settings
from fsqlfly.settings import UPLOAD_ROOT_DIR, FSQLFLY_JOB_LOG_FILE

is_login = False
user = dict(code=200, name='flink', status='ok', currentAuthority='admin', type='password',
            avatar='https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png')

support_upload = ['logo', 'file']
upload_dirs = {x: os.path.join(UPLOAD_ROOT_DIR, x) for x in support_upload}
_ = [os.makedirs(x, exist_ok=True) for x in upload_dirs.values()]

FileMagic = magic.Magic(mime=True, uncompress=True)


class UploadHandler(BaseHandler):
    @authenticated
    def get(self, path: str):
        if not any(map(lambda x: path.startswith(x), support_upload)):
            raise tornado.web.HTTPError(status_code=404)
        full_path = os.path.join(UPLOAD_ROOT_DIR, path)
        if not os.path.exists(full_path):
            self.write_error(RespCode.APIFail)
        mime = FileMagic.from_file(full_path)
        self.set_header('content-type', mime)
        self.write(open(full_path, "rb").read())
        self.finish()

    @authenticated
    def post(self):
        files = self.request.files
        key = list(files.keys())[0]
        if key not in support_upload:
            self.write_error(RespCode.APIFail)
        upload_file = files[key][0]

        _, tem_f = mkstemp(suffix=upload_file.filename, dir=upload_dirs[key])
        with open(tem_f, 'wb+') as out:
            out.write(upload_file.body)
        real_path = '/upload/' + key + '/' + os.path.basename(tem_f)
        return self.write_json(create_response(data={"realPath": real_path}))


class LogHandler(BaseHandler):
    @authenticated
    def get(self):
        if not os.path.exists(FSQLFLY_JOB_LOG_FILE):
            raise tornado.web.HTTPError(status_code=404)
        self.set_header('content-type', 'text')
        self.write(open(FSQLFLY_JOB_LOG_FILE, "rb").read())
        self.finish()


class BlankHandler(BaseHandler):
    def get(self):
        self.set_header('content-type', 'text')
        self.write('...')
        self.finish()


default_handlers = [
    (r'/api/upload', UploadHandler),
    (r'/api/log', LogHandler),
    (r'/api/blank', BlankHandler),
    (r'/upload/(?P<path>.+)', UploadHandler),
]
