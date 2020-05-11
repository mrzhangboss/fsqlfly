import os
import hashlib
import logging
import logzero
from logzero import logger
from os.path import join
from dotenv import load_dotenv
from pathlib import Path
from terminado.management import NamedTermManager
from sqlalchemy import create_engine


def generate_cookie_secret(s: str, typ: str = '___cookie_secret') -> str:
    md5 = hashlib.md5()
    md5.update(f'{s}{typ}'.encode())
    return md5.hexdigest()


BASE_DIR = os.path.expanduser('~')
ENV_FILE_PATH_FROM_LOCAL_ENV = os.environ.get('FSQLFLY')
ENV_FILE_PATH = join(BASE_DIR, '.fsqlfly')
if ENV_FILE_PATH_FROM_LOCAL_ENV and os.path.exists(ENV_FILE_PATH_FROM_LOCAL_ENV):
    logger.debug('Change Env File to {}'.format(ENV_FILE_PATH_FROM_LOCAL_ENV))
    ENV_FILE_PATH = ENV_FILE_PATH_FROM_LOCAL_ENV
if os.path.exists(ENV_FILE_PATH) and os.path.isfile(ENV_FILE_PATH):
    logging.debug("Load Env File From {} ".format(ENV_FILE_PATH))
    load_dotenv(dotenv_path=Path(ENV_FILE_PATH))
else:
    logging.debug("Not Found Valid Env File ".format(ENV_FILE_PATH))

ENV = os.environ.get
FSQLFLY_DEBUG = ENV('FSQLFLY_DEBUG') is not None
FSQLFLY_SAVE_MODE_DISABLE = ENV('FSQLFLY_SAVE_MODE_DISABLE') is not None
if FSQLFLY_DEBUG:
    logzero.loglevel(logging.DEBUG)

FSQLFLY_PASSWORD = ENV('FSQLFLY_PASSWORD', 'password')
logger.debug('FSQLFLY_PASSWORD is {}'.format(FSQLFLY_PASSWORD))
FSQLFLY_TOKEN = generate_cookie_secret(FSQLFLY_PASSWORD, '')
FSQLFLY_TOKEN_BYTE = FSQLFLY_TOKEN.encode()
logger.debug('FSQLFLY_TOKEN_BYTE is {}'.format(FSQLFLY_TOKEN_BYTE))

FSQLFLY_COOKIE_SECRET = generate_cookie_secret(FSQLFLY_PASSWORD)

FSQLFLY_DB_URL = ENV('FSQLFLY_DB_URL')

assert FSQLFLY_DB_URL, 'FSQLFLY_DB_URL must not be null'
ENGINE = create_engine(FSQLFLY_DB_URL, echo=FSQLFLY_DEBUG)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FSQLFLY_UPLOAD_DIR = ENV('FSQLFLY_UPLOAD_DIR', join(os.path.expanduser('~'), '.fsqlfly_upload'))
if not os.path.exists(FSQLFLY_UPLOAD_DIR):
    logger.debug('Create Upload Base Dir {}'.format(FSQLFLY_UPLOAD_DIR))
    os.makedirs(FSQLFLY_UPLOAD_DIR)
UPLOAD_ROOT_DIR = join(FSQLFLY_UPLOAD_DIR, 'upload')

FSQLFLY_STATIC_ROOT = ENV('FSQLFLY_STATIC_ROOT', join(ROOT_DIR, 'static'))
FSQLFLY_FINK_HOST = ENV('FSQLFLY_FINK_HOST', 'http://localhost:8081')
FSQLFLY_JOB_DAEMON_FREQUENCY = int(ENV('FSQLFLY_JOB_DAEMON_FREQUENCY', '30'))
FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY = int(ENV('FSQLFLY_JOB_DAEMON_MAX_TRY_ONE_DAY', '3'))

assert os.path.exists(FSQLFLY_STATIC_ROOT), "FSQLFLY_STATIC_ROOT ({}) not set correct".format(FSQLFLY_STATIC_ROOT)
INDEX_HTML_PATH = join(FSQLFLY_STATIC_ROOT, 'index.html')
assert os.path.exists(INDEX_HTML_PATH), "FSQLFLY_STATIC_ROOT ({}) can't find index.html".format(FSQLFLY_STATIC_ROOT)
INDEX_HTML = open(INDEX_HTML_PATH, 'rb').read()

FSQLFLY_FLINK_BIN_DIR = ENV('FSQLFLY_FLINK_BIN_DIR', '/opt/flink/bin')
assert os.path.exists(FSQLFLY_FLINK_BIN_DIR), "FSQLFLY_FLINK_BIN_DIR ({}) not exists, please confirm".format(
    FSQLFLY_FLINK_BIN_DIR)
FSQLFLY_FLINK_BIN = join(FSQLFLY_FLINK_BIN_DIR, 'sql-client.sh')

FSQLFLY_FLINK_MAX_TERMINAL = int(ENV('FSQLFLY_FLINK_MAX_TERMINAL', '100'))
FSQLFLY_WEB_PORT = int(ENV('FSQLFLY_WEB_PORT', '8082'))

TERMINAL_MANAGER = NamedTermManager(
    shell_command=[FSQLFLY_FLINK_BIN, 'embedded'],
    max_terminals=FSQLFLY_FLINK_MAX_TERMINAL)

TERMINAL_OPEN_NAME = '__NEED_OPEN_'
FSQLFLY_JOB_LOG_DIR = ENV('FSQLFLY_JOB_LOG_DIR', '/tmp/fsqlfly_job_log')
FSQLFLY_JOB_LOG_FILE = join(FSQLFLY_JOB_LOG_DIR, 'job_damon.log')
os.makedirs(FSQLFLY_JOB_LOG_DIR, exist_ok=True)

TEMP_TERMINAL_HEAD = '0__TEMPORARY__'

# email

FSQLFLY_MAIL_ENABLE = ENV('FSQLFLY_MAIL_ENABLE') is not None
FSQLFLY_MAIL_HOST = ENV('FSQLFLY_MAIL_HOST')
FSQLFLY_MAIL_USER = ENV('FSQLFLY_MAIL_USER')
FSQLFLY_MAIL_PASSWORD = ENV('FSQLFLY_MAIL_PASSWORD')
FSQLFLY_MAIL_RECEIVERS = ENV('FSQLFLY_MAIL_RECEIVERS')
