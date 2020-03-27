import os
import hashlib
import logging
from dotenv import load_dotenv
from pathlib import Path
from peewee import MySQLDatabase, SqliteDatabase, PostgresqlDatabase
from playhouse.cockroachdb import CockroachDatabase
from playhouse.db_url import connect


def generate_cookie_secret(s: str) -> str:
    md5 = hashlib.md5()
    md5.update(f'{s}___cookie_secret'.encode())
    return md5.hexdigest()


BASE_DIR = os.path.expanduser('~')
ENV_FILE_PATH = os.path.join(BASE_DIR, '.fsqlfly')
if os.path.exists(ENV_FILE_PATH) and os.path.isfile(ENV_FILE_PATH):
    logging.debug("Load Env File From {} ".format(ENV_FILE_PATH))
    load_dotenv(dotenv_path=Path(ENV_FILE_PATH))

ENV = os.environ.get

FSQLFLY_PASSWORD = ENV('FSQLFLY_PASSWORD', 'password')

FSQLFLY_COOKIE_SECRET = generate_cookie_secret(FSQLFLY_PASSWORD)

FSQLFLY_DB_URL = ENV('FSQLFLY_DB_URL')
FSQLFLY_DB_TYPE = ENV('FSQLFLY_DB_TYPE', 'sqlite')
FSQLFLY_DB_FILE = ENV('FSQLFLY_DB_FILE', 'db.sqlite3')
FSQLFLY_DATABASE = ENV('FSQLFLY_DATABASE', 'test')
FSQLFLY_DB_PASSWORD = ENV('FSQLFLY_DB_PASSWORD', 'xxx')
FSQLFLY_DB_USER = ENV('FSQLFLY_DB_USER', 'root')
FSQLFLY_DB_HOST = ENV('FSQLFLY_DB_HOST', 'localhost')
FSQLFLY_DB_PORT = int(ENV('FSQLFLY_DB_PORT', '3306'))

if FSQLFLY_DB_URL is not None:
    DATABASE = connect(FSQLFLY_DB_URL)
elif FSQLFLY_DB_TYPE == 'sqlite':
    DATABASE = SqliteDatabase(FSQLFLY_DB_FILE)
else:
    assert FSQLFLY_DB_TYPE in (
        'mysql', 'postgresql', 'cockroach'), 'env FSQLFLY_DB_TYPE must in (sqlite|mysql|postgresql|cockroach)'
    db_classes = {
        'mysql': MySQLDatabase,
        'postgresql': PostgresqlDatabase,
        'cockroach': CockroachDatabase
    }
    db_class = db_classes[FSQLFLY_DB_TYPE]
    DATABASE = db_class(database=FSQLFLY_DATABASE,
                        password=FSQLFLY_DB_PASSWORD, user=FSQLFLY_DB_USER, host=FSQLFLY_DB_HOST, port=FSQLFLY_DB_PORT)
