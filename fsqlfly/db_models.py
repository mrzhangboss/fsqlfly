import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from fsqlfly.connection_manager import SUPPORT_MANAGER
from sqlalchemy_utils import ChoiceType
from logzero import logger

_Base = declarative_base()

CONNECTION_TYPE = ChoiceType([(k, str(v)) for k, v in SUPPORT_MANAGER.items()], impl=String(16))
FILE_TYPE = ChoiceType([(k, k) for k in ['savepoint', 'function', 'upload', 'resource']], impl=String(16))
CASCADE = "delete, delete-orphan"


class Base(_Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=sa.func.now())
    updated_at = Column(DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now())

    def as_dict(self):
        return {k: v for k, v in vars(self).items() if k != '_sa_instance_state'}


class Connection(Base):
    __tablename__ = 'connection'
    name = Column(String(32), nullable=False, unique=True)
    url = Column(Text, nullable=False)
    type = Column(CONNECTION_TYPE, nullable=False)
    info = Column(Text)
    connector = Column(Text, nullable=False)
    catalog = Column(Text)
    is_hidden = Column(Boolean, default=False)
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
    connection = relationship('Connection', backref=backref('schemas', cascade=CASCADE), cascade=CASCADE,
                              single_parent=True)
    father_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    father = relationship('SchemaEvent', backref='children', remote_side='SchemaEvent.id')
    type = Column(CONNECTION_TYPE, nullable=False)
    version = Column(Integer, nullable=False)
    comment = Column(Text)
    primary_key = Column(String(64))
    fields = Column(Text)
    partitionable = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)


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
    is_hidden = Column(Boolean, default=False)


class ResourceName(Base):
    __tablename__ = 'resource_name'
    name = Column(String(128), nullable=False)
    info = Column(Text)
    database = Column(String(64), nullable=True)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship(Connection, backref=backref('resource_names', cascade=CASCADE), cascade=CASCADE,
                              single_parent=True)
    schema_version = relationship(SchemaEvent, backref=backref('resource_names', cascade=CASCADE), cascade=CASCADE,
                                  single_parent=True)
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    full_name = Column(String(2048), nullable=False, unique=True)
    is_hidden = Column(Boolean, default=False)


class ResourceTemplate(Base):
    __tablename__ = 'resource_template'
    name = Column(String(128), nullable=False)
    info = Column(Text)
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    full_name = Column(String(2048), nullable=False, unique=True)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship('Connection', backref=backref('templates', cascade=CASCADE), cascade=CASCADE,
                              single_parent=True)
    resource_name_id = Column(Integer, ForeignKey('resource_name.id'), nullable=False)
    resource_name = relationship(ResourceName, backref=backref('templates', cascade=CASCADE), cascade=CASCADE,
                                 single_parent=True)
    schema_version = relationship(SchemaEvent, backref=backref('templates', cascade=CASCADE), cascade=CASCADE,
                                  single_parent=True)
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'), nullable=True)
    is_hidden = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    config = Column(Text)


class ResourceVersion(Base):
    __tablename__ = 'resource_version'
    __table_args__ = (
        UniqueConstraint('template_id', 'version'),
    )
    name = Column(String(128), nullable=True)
    info = Column(Text)
    full_name = Column(String(2048), nullable=False, unique=True)
    is_system = Column(Boolean, default=False)
    is_latest = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    version = Column(Integer, nullable=False, default=0)
    connection_id = Column(Integer, ForeignKey('connection.id'), nullable=False)
    connection = relationship(Connection, backref=backref('versions', cascade=CASCADE), cascade=CASCADE,
                              single_parent=True)
    resource_name_id = Column(Integer, ForeignKey('resource_name.id'), nullable=False)
    resource_name = relationship(ResourceName, backref=backref('versions', cascade=CASCADE), cascade=CASCADE,
                                 single_parent=True)
    template_id = Column(Integer, ForeignKey('resource_template.id'), nullable=False)
    template = relationship(ResourceTemplate, backref=backref('versions', cascade=CASCADE), cascade=CASCADE,
                            single_parent=True)
    schema_version = relationship(SchemaEvent, backref=backref('versions', cascade=CASCADE), cascade=CASCADE,
                                  single_parent=True)
    schema_version_id = Column(Integer, ForeignKey('schema_event.id'))
    config = Column(Text)


class Namespace(Base):
    __tablename__ = 'namespace'
    name = Column(String(256), unique=True)
    info = Column(Text)
    avatar = Column(Text)
    is_hidden = Column(Boolean, default=True)
    is_daemon = Column(Boolean, default=False)


class FileResource(Base):
    __tablename__ = 'file_resource'
    name = Column(String(1024), unique=True, nullable=False)
    type = Column(FILE_TYPE, nullable=False)
    info = Column(Text)
    real_path = Column(String(2048))
    transform_id = Column(Integer, ForeignKey('transform.id'))
    transform = relationship('Transform', backref=backref('savepoint', cascade=CASCADE), cascade=CASCADE,
                             single_parent=True)
    is_hidden = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)


class Functions(Base):
    __tablename__ = 'functions'
    name = Column(String(256), unique=True, nullable=False)
    class_name = Column(String(512), nullable=False)
    constructor_config = Column(Text)
    resource_id = Column(Integer, ForeignKey('file_resource.id'), nullable=False)
    resource = relationship(FileResource, backref=backref('functions', cascade=CASCADE), cascade=CASCADE,
                            single_parent=True)
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
    namespace = relationship(Namespace, backref=backref('transforms'), cascade="delete, delete-orphan",
                             single_parent=True)
    is_hidden = Column(Boolean, default=True)
    is_daemon = Column(Boolean, default=False)

    class Meta:
        table_name = "transform"


def delete_all_tables(engine, force: bool = False):
    if not force:
        word = input('Are you delete all tables (Y/n)')
        if word.strip().upper() != 'Y':
            return
    logger.info("begin delete all tables")
    Base.metadata.drop_all(engine)


def create_all_tables(engine):
    Base.metadata.create_all(engine)
