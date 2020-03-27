import logging
import datetime
from playhouse.shortcuts import model_to_dict
from peewee import *
from fsqlfly.settings import DATABASE


class BaseModel(Model):
    is_deleted = BooleanField(default=False)
    is_publish = BooleanField(default=False)
    is_available = BooleanField(default=True)
    create_at = DateTimeField(default=datetime.datetime.now)
    update_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

    def save(self, *args, **kwargs):
        self.update_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    def to_dict(self):
        return {k: str(v) if isinstance(v, datetime.datetime) else v for k, v in model_to_dict(self).items()}


class Namespace(BaseModel):
    name = CharField(max_length=256, unique=True)
    info = CharField(max_length=2048, null=True)
    avatar = CharField(max_length=2048, null=True)

    class Meta:
        table_name = "namespace"


class FileResource(BaseModel):
    unique_name = CharField(max_length=128, unique=True)
    info = CharField(max_length=1024, null=True)
    real_path = CharField(max_length=2048)

    class Meta:
        table_name = "file_resource"


class Resource(BaseModel):
    name = CharField(max_length=256, unique=True)
    info = CharField(max_length=2048, null=True)
    typ = CharField(max_length=16)
    yaml = TextField(default='')
    namespace = ForeignKeyField(Namespace, on_delete='NO ACTION', null=True)

    class Meta:
        table_name = "resource"


class Functions(BaseModel):
    name = CharField(max_length=256, unique=True)
    function_from = CharField(max_length=16, default="class")
    class_name = CharField(max_length=256)
    constructor_config = CharField(max_length=2048)
    resource = ForeignKeyField(FileResource, on_delete='NO ACTION')

    class Meta:
        table_name = "functions"


class Transform(BaseModel):
    name = CharField(max_length=256, unique=True)
    info = CharField(max_length=2048, null=True)
    sql = TextField()
    require = TextField()
    yaml = TextField(default='')
    namespace = ForeignKeyField(Namespace, on_delete='NO ACTION', null=True)

    class Meta:
        table_name = "transform"


TABLES = [Namespace, Resource, FileResource, Resource, Transform, Functions]


def delete_all_tables(force: bool = False):
    if not force:
        word = input('Are you delete all tables (Y/n)')
        if word.strip().upper() != 'Y':
            return
    logging.info("begin delete all tables")
    DATABASE.drop_tables(TABLES)


def create_all_tables():
    DATABASE.create_tables(TABLES)
