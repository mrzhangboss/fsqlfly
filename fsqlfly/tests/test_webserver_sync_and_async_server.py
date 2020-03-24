import time
from tornado.ioloop import IOLoop
from tornado import gen
import tormysql
import tornado.web
import asyncio
from peewee_async import Manager, PostgresqlDatabase, MySQLDatabase
from playhouse.db_url import connect
from tornado.web import Application

loop = asyncio.new_event_loop()
user, password, host, db = 'root', 'zhanglun', 'localhost', 'sample'
database = connect(f'mysql://{user}:{password}@{host}:3306/{db}')
connection_pool = tormysql.helpers.ConnectionPool(
    max_connections=20,  # max open connections
    idle_seconds=7200,  # conntion idle timeout time, 0 is not timeout
    wait_connection_timeout=3,  # wait connection timeout
    host=host,
    user=user,
    passwd=password,
    db=db,
    charset="utf8"
)

from peewee import Model, CharField, DateField
from datetime import datetime
from playhouse.shortcuts import model_to_dict


class BaseModel(Model):
    class Meta:
        database = database


class Person(BaseModel):
    name = CharField()
    create_at = DateField(default=datetime.now)


database.drop_tables([Person], safe=True)
database.create_tables([Person], safe=True)
for i in range(1000):
    Person.create(name=f'test {i}')

from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor


def get_all_person():
    return str(list(Person.select().objects()))


class AsyncHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor()

    async def get(self):
        person = await self.get_person()
        self.write(person)

    @run_on_executor
    def get_person(self):
        return get_all_person()


class SyncHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(get_all_person())


class PoolHandler(tornado.web.RequestHandler):

    async def get(self):
        cursor = await connection_pool.execute("select * from person")
        data = cursor.fetchall()
        self.write(str(data))


def make_app():
    return tornado.web.Application([
        (r"/sync", SyncHandler),
        (r"/async", AsyncHandler),
        (r"/pool_async", PoolHandler),
    ],
        debug=True)


app = make_app()
app.listen(8889)

if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().start()
