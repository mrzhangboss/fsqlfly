import sqlalchemy as sa
from configparser import ConfigParser
from typing import Any, Optional, Union, Type
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean, Text, UniqueConstraint, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from fsqlfly.common import SUPPORT_MANAGER, SUPPORT_TABLE_TYPE
from sqlalchemy_utils import ChoiceType, Choice
from logzero import logger

_Base = declarative_base()

CONNECTION_TYPE = ChoiceType([(k, k) for k in SUPPORT_MANAGER], impl=String(16))
TABLE_TYPE = ChoiceType([(k, k) for k in SUPPORT_TABLE_TYPE], impl=String(8))


def _b(x: str):
    return backref(x, cascade="delete, delete-orphan")


class SaveDict(dict):
    @property
    def id(self):
        return self.get('id')


_DEFAULT_CONFIG = """
[db]
insert_primary_key = false

[kafka]
process_time_enable = true
process_time_name = flink_process_time
rowtime_enable = true
rowtime_from = MYSQL_DB_EXECUTE_TIME


"""


class Base(_Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=sa.func.now())
    updated_at = Column(DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    is_locked = Column(Boolean, default=False)

    def as_dict(self) -> SaveDict:
        def _convert(v: Any) -> Any:
            if isinstance(v, Choice):
                return v.code
            return v

        return SaveDict({column.name: _convert(getattr(self, column.name)) for column in self.__table__.columns})

    @classmethod
    def get_default_config_parser(cls) -> ConfigParser:
        config = ConfigParser()
        config.read_string(_DEFAULT_CONFIG)
        return config

    def get_config_parser(self) -> ConfigParser:
        return self.get_default_config_parser()

    def get_config(self, name: str, section: str,
                   typ: Optional[Union[Type[int], Type[float], Type[float], Type[str]]] = None) -> Any:
        cache_name = '__config_parser__'
        if not hasattr(self, cache_name):
            setattr(self, cache_name, self.get_config_parser())
        parser = getattr(self, cache_name)
        secret = parser[section]
        if typ:
            if typ is int:
                return secret.getint(name)
            elif typ is float:
                return secret.getint(name)
            elif typ is bool:
                return secret.getboolean(name)
        return secret[name]


class Connection(Base):
    __tablename__ = 'connection'
    name = Column(String(32), nullable=False, unique=True)
    update_interval = Column(Integer, default=0)
    url = Column(Text, nullable=False)
    type = Column(CONNECTION_TYPE, nullable=False)
    info = Column(Text)
    connector = Column(Text, nullable=False)
    config = Column(Text)
    include = Column(String(2048))
    exclude = Column(String(2048))
    is_active = Column(Boolean, default=False)

    def get_config(self, name: str, section: Optional[str] = None,
                   typ: Optional[Union[Type[int], Type[float], Type[float], Type[str]]] = None) -> Any:
        return super(Connection, self).get_config(name, section=section if section else self.type, typ=typ)

    def get_config_parser(self) -> ConfigParser:
        parser = super(Connection, self).get_config_parser()
        if self.config and self.config.strip():
            parser.read_string(self.config)

        return parser


class SchemaEvent(Base):
    __tablename__ = 'schema_event'
    __table_args__ = (
        UniqueConstraint('connection_id', 'name', 'database', 'version'),
    )
    name = Column(String(128), nullable=False)
    info = Column(Text)
    database = Column(String(64), nullable=True)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship('Connection', backref=_b('schemas'))
    father_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    father = relationship('SchemaEvent', backref=_b('children'), remote_side='SchemaEvent.id')
    version = Column(Integer, nullable=False, default=0)
    comment = Column(Text)
    primary_key = Column(String(64))
    fields = Column(Text)
    partitionable = Column(Boolean, default=False)


class Connector(Base):
    __tablename__ = 'connector'
    name = Column(String(128), nullable=False, unique=True)
    info = Column(Text)
    source_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    source = relationship(Connection, foreign_keys=source_id, passive_deletes=False)
    target = relationship(Connection, foreign_keys=target_id, passive_deletes=False)
    config = Column(Text)
    generate_sql = Column(Text)


class ResourceName(Base):
    __tablename__ = 'resource_name'
    __table_args__ = (
        UniqueConstraint('connection_id', 'name', 'database'),
    )
    name = Column(String(128), nullable=False)
    info = Column(Text)
    database = Column(String(64), nullable=True)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship(Connection, backref=_b('resource_names'))
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    schema_version = relationship(SchemaEvent, backref=_b('resource_names'), foreign_keys=schema_version_id)
    latest_schema_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    config = Column(Text)
    is_latest = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    full_name = Column(String(512), nullable=False, unique=True)

    def get_include(self):
        return self.database + '.' + self.name if self.database else self.name

    @classmethod
    def generate_full_name(cls, connection_name: str, database: Optional[str], name: str):
        return connection_name + (database + '.' + name if database else name)

    def get_config_parser(self) -> ConfigParser:
        parser = self.connection.get_config_parser()
        if self.config and self.config.strip():
            parser.read_string(self.config)

        return parser

    def get_config(self, name: str, section: Optional[str] = None,
                   typ: Optional[Union[Type[int], Type[float], Type[float], Type[str]]] = None) -> Any:
        return super(ResourceName, self).get_config(name, section=section if section else self.connection.type, typ=typ)


class ResourceTemplate(Base):
    __tablename__ = 'resource_template'
    __table_args__ = (
        UniqueConstraint('resource_name_id', 'name'),
    )
    name = Column(String(128), nullable=False)
    type = Column(TABLE_TYPE, nullable=False)
    info = Column(Text)
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    full_name = Column(String(512), nullable=False, unique=True)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship('Connection', backref=_b('templates'))
    resource_name_id = Column(Integer, ForeignKey('resource_name.id'), nullable=False)
    resource_name = relationship(ResourceName, backref=_b('templates'))
    schema_version = relationship(SchemaEvent, backref=_b('templates'))
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    config = Column(Text)

    @classmethod
    def get_full_name(cls, resource_name: ResourceName, name: str) -> str:
        return resource_name.full_name + '.' + name


class ResourceVersion(Base):
    __tablename__ = 'resource_version'
    __table_args__ = (
        UniqueConstraint('template_id', 'version'),
    )
    name = Column(String(128), nullable=False, default='latest')
    info = Column(Text)
    full_name = Column(String(512), nullable=False, unique=True)
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    is_latest = Column(Boolean, default=False)
    version = Column(Integer, nullable=False, default=0)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship(Connection, backref=_b('versions'))
    resource_name_id = Column(Integer, ForeignKey('resource_name.id'), nullable=False)
    resource_name = relationship(ResourceName, backref=_b('versions'))
    template_id = Column(Integer, ForeignKey('resource_template.id'), nullable=False)
    template = relationship(ResourceTemplate, backref=_b('versions'))
    schema_version = relationship(SchemaEvent, backref=_b('versions'))
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'))
    config = Column(Text)
    cache = Column(Text)

    @classmethod
    def get_full_name(cls, template: ResourceTemplate, name: str = 'latest'):
        return template.full_name + '.' + name


class Namespace(Base):
    __tablename__ = 'namespace'
    name = Column(String(256), unique=True)
    info = Column(Text)
    avatar = Column(Text)
    is_daemon = Column(Boolean, default=False)


class FileResource(Base):
    __tablename__ = 'file_resource'
    name = Column(String(512), unique=True, nullable=False)
    info = Column(Text)
    real_path = Column(Text)
    is_system = Column(Boolean, default=False)


class Functions(Base):
    __tablename__ = 'functions'
    name = Column(String(256), unique=True, nullable=False)
    class_name = Column(String(512), nullable=False)
    constructor_config = Column(Text)
    resource_id = Column(Integer, ForeignKey('file_resource.id'), nullable=False)
    resource = relationship(FileResource, backref=_b('functions'))
    is_active = Column(Boolean, default=True)

    class Meta:
        table_name = "functions"


class Transform(Base):
    __tablename__ = 'transform'
    name = Column(String(256), unique=True, nullable=False)
    info = Column(Text)
    sql = Column(Text, nullable=True)
    require = Column(Text)
    yaml = Column(Text)
    namespace_id = Column(Integer, ForeignKey('namespace.id'), nullable=True)
    namespace = relationship(Namespace, backref=_b('transforms'))
    is_daemon = Column(Boolean, default=False)

    class Meta:
        table_name = "transform"


class TransformSavepoint(Base):
    __tablename__ = 'transform_savepoint'
    name = Column(String(1024), nullable=False)
    path = Column(Text, nullable=False)
    info = Column(Text)
    snapshot = Column(Text)
    transform_id = Column(Integer, ForeignKey('transform.id'))
    transform = relationship('Transform', backref=_b('savepoint'))


def delete_all_tables(engine, force: bool = False):
    if not force:
        word = input('Are you delete all tables (Y/n)')
        if word.strip().upper() != 'Y':
            return
    logger.info("begin delete all tables")
    Base.metadata.drop_all(engine)


def create_all_tables(engine):
    Base.metadata.create_all(engine)


__all__ = ['create_all_tables', 'delete_all_tables', 'Base', 'Connection',
           'SchemaEvent', 'Connector', 'ResourceName', 'ResourceVersion', 'ResourceTemplate',
           'Namespace', 'FileResource', 'Transform', 'Functions', 'TransformSavepoint', 'SaveDict']
