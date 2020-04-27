import sqlalchemy as sa
from typing import Any
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean, Text, UniqueConstraint, event
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from fsqlfly.connection_manager import SUPPORT_MANAGER, SUPPORT_TABLE_TYPE
from sqlalchemy_utils import ChoiceType, Choice
from logzero import logger

_Base = declarative_base()

CONNECTION_TYPE = ChoiceType([(k, str(v)) for k, v in SUPPORT_MANAGER.items()], impl=String(16))
TABLE_TYPE = ChoiceType([(k, k) for k in SUPPORT_TABLE_TYPE], impl=String(8))


def _b(x: str):
    return backref(x, cascade="delete, delete-orphan")


class Base(_Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=sa.func.now())
    updated_at = Column(DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())
    is_locked = Column(Boolean, default=False)

    def as_dict(self):
        def _convert(v: Any) -> Any:
            if isinstance(v, Choice):
                return v.code
            return v

        return {column.name: _convert(getattr(self, column.name)) for column in self.__table__.columns}


class Connection(Base):
    __tablename__ = 'connection'
    name = Column(String(32), nullable=False, unique=True)
    update_interval = Column(Integer, default=0)
    url = Column(Text, nullable=False)
    type = Column(CONNECTION_TYPE, nullable=False)
    info = Column(Text)
    connector = Column(Text, nullable=False)
    include = Column(String(2048))
    exclude = Column(String(2048))
    is_active = Column(Boolean, default=False)


class SchemaEvent(Base):
    __tablename__ = 'schema_event'
    __table_args__ = (
        UniqueConstraint('connection_id', 'name', 'database', 'version'),
    )
    name = Column(String(128), nullable=False)
    info = Column(Text)
    database = Column(String(64), nullable=True)
    connection_id = Column(Integer, ForeignKey('connection.id'))
    connection = relationship('Connection', backref=_b('schemas'))
    father_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    father = relationship('SchemaEvent', backref=_b('children'), remote_side='SchemaEvent.id')
    type = Column(CONNECTION_TYPE, nullable=False)
    version = Column(Integer, nullable=False)
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
    name = Column(String(128), nullable=False)
    info = Column(Text)
    database = Column(String(64), nullable=True)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship(Connection, backref=_b('resource_names'))
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    schema_version = relationship(SchemaEvent, backref=_b('resource_names'), foreign_keys=schema_version_id)
    latest_schema_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    is_latest = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    full_name = Column(String(512), nullable=False, unique=True)


class ResourceTemplate(Base):
    __tablename__ = 'resource_template'
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


class ResourceVersion(Base):
    __tablename__ = 'resource_version'
    __table_args__ = (
        UniqueConstraint('template_id', 'version'),
    )
    name = Column(String(128), nullable=True)
    info = Column(Text)
    full_name = Column(String(512), nullable=False, unique=True)
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
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
           'Namespace', 'FileResource', 'Transform', 'Functions', 'TransformSavepoint']
