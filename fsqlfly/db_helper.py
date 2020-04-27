from fsqlfly.db_models import *
import traceback
from sqlalchemy import and_, event
from sqlalchemy.engine import Engine
from functools import wraps
from typing import Callable, Type, Optional, List, Union
from fsqlfly import settings
from fsqlfly.common import DBRes
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.orm.session.query import Query

SUPPORT_MODELS = {
    'connection': Connection,
    'connector': Connector,
    'schema': SchemaEvent,
    'name': ResourceName,
    'template': ResourceTemplate,
    'version': ResourceVersion,
    'file': FileResource,
    'functions': Functions,
    'transform': Transform,
    'namespace': Namespace,
    'savepoint': TransformSavepoint

}


class DBSession:
    engine = None
    _Session = None

    @classmethod
    def init_engine(cls, engine: Engine):
        cls.engine = engine
        cls._Session = sessionmaker(bind=engine)

    @classmethod
    def get_session(cls) -> Session:
        assert cls.engine is not None
        return cls._Session()


def session_add(func: Callable) -> Callable:
    @wraps(func)
    def _add_session(*args, **kwargs):
        session = kwargs['session'] if 'session' in kwargs else DBSession.get_session()
        try:
            res = func(*args, session=session, **kwargs)
            session.commit()
            return res
        except Exception:
            session.rollback()
            err = traceback.format_exc()
            return DBRes.sever_error(msg=f'meet {err}')
        finally:
            session.close()

    return _add_session


def filter_not_support(func: Callable) -> Callable:
    @wraps(func)
    def _call_(*args, **kwargs):
        model = kwargs['model'] if 'model' in kwargs else args[1]
        if model not in SUPPORT_MODELS:
            return DBRes.api_error(msg=f'{model} not support')
        base = SUPPORT_MODELS[model]
        return func(*args, base=base, **kwargs)

    return _call_


class DBDao:
    @classmethod
    @session_add
    @filter_not_support
    def update(cls, model: str, pk: int, obj: dict, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        assert session is not None
        first = session.query(base).filter(base.id == pk).first()
        if first is None:
            return DBRes.not_found()

        if first.is_locked:
            return DBRes.resource_locked()

        for k, v in obj.items():
            if k not in ['id', 'create_at', 'update_at']:
                setattr(first, k, v)
        return DBRes(data=first.as_dict())

    @classmethod
    @session_add
    @filter_not_support
    def create(cls, model: str, obj: dict, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        db_obj = base(**obj)
        session.add(db_obj)
        session.commit()
        return DBRes(data=db_obj.as_dict())

    @classmethod
    def build_and(cls, data: dict, base: Type, query: Query) -> Query:
        kvs = [getattr(base, k) == v for k, v in data.items()]
        if len(kvs) > 1:
            query = query.filter(and_(*kvs))
        else:
            query = query.filter(kvs[0])
        return query

    @classmethod
    @session_add
    @filter_not_support
    def get(cls, model: str, *args, session: Session, base: Type[Base], filter_: Optional[dict] = None,
            **kwargs) -> DBRes:
        query = session.query(base)
        if filter_:
            query = cls.build_and(filter_, base, query)
        return DBRes(data=[x.as_dict() for x in query.all()])

    @classmethod
    @session_add
    @filter_not_support
    def delete(cls, model: str, pk: int, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        if settings.FSQLFLY_SAVE_MODE_DISABLE:
            obj = session.query(base).get(pk)
            session.delete(obj)
            return DBRes(data=obj.id)
        else:
            return DBRes.sever_error('Not Support Delete when FSQLFLY_SAVE_MODE_DISABLE not set')

    @classmethod
    @session_add
    def bulk_insert(cls, data: list, *args, session: Session, **kwargs):
        session.add_all(data)
        return DBRes(data=len(data))

    @classmethod
    @session_add
    def count(cls, base: Type[Base], *args, session: Session, **kwargs) -> int:
        return session.query(base).count()

    @classmethod
    @session_add
    def get_transform(cls, pk: Optional[int] = None, *args, session: Session, **kwargs) -> Union[List[Base], Base]:
        query = session.query(Transform)
        if pk:
            return query.filter(Transform.id == pk).first()
        return query.all()

    @classmethod
    @session_add
    def save(cls, obj: Type[Base], *args, session: Session, **kwargs) -> Type[Base]:
        session.add(obj)
        session.commit()
        return obj

    @classmethod
    @session_add
    def upsert_schema_event(cls, obj: SchemaEvent, *args, session: Session, **kwargs) -> SchemaEvent:
        query = session.query(SchemaEvent).filter(and_(SchemaEvent.database == obj.database,
                                                       SchemaEvent.name == obj.name,
                                                       SchemaEvent.connection == obj.connection,
                                                       SchemaEvent.fields == obj.fields))
        first = query.order_by(SchemaEvent.version.desc()).first()
        if first:
            obj.version = first.version + 1
            obj.father = first
        session.add(obj)
        session.commit()
        return obj

    @classmethod
    @session_add
    def upsert_resource_name(cls, obj: ResourceName, *args, session: Session, **kwargs) -> ResourceName:
        query = session.query(ResourceName).filter(and_(ResourceName.full_name == obj.full_name,
                                                        ResourceName.connection == obj.connection))
        res = first = query.first()
        if first:
            res.latest_schema_id = obj.latest_schema_id
            res.info = obj.info
            res.is_latest = first.latest_schema_id == obj.schema_version_id
        else:
            res = obj
        session.add(res)
        session.commit()
        return res

    @classmethod
    @session_add
    def upsert_resource_template(cls, obj: ResourceTemplate, *args, session: Session, **kwargs) -> ResourceTemplate:
        query = session.query(ResourceTemplate).filter(and_(ResourceTemplate.name == obj.name,
                                                            ResourceTemplate.connection == obj.connection,
                                                            ResourceTemplate.resource_name == obj.resource_name))
        res = first = query.order_by(SchemaEvent.version.desc()).first()
        if first:
            res.config = obj.config
            res.info = obj.info
            res.is_system = obj.is_system
            res.is_default = obj.is_default
            res.full_name = obj.full_name
            res.is_latest = first.latest_schema_id == obj.schema_version_id
        else:
            res = obj
        session.add(res)
        session.commit()
        return obj

    @classmethod
    @session_add
    def upsert_resource_version(cls, obj: ResourceVersion, *args, session: Session, **kwargs) -> ResourceVersion:
        query = session.query(ResourceVersion).filter(and_(ResourceVersion.name == obj.name,
                                                           ResourceVersion.connection == obj.connection,
                                                           ResourceVersion.resource_name == obj.resource_name,
                                                           ResourceVersion.template == obj.template))
        first = query.order_by(ResourceVersion.version.desc()).first()
        if first:
            first.version += 1
            first.config = obj.config
            first.cache = obj.cache
        else:
            first = obj

        session.add(first)
        session.commit()
        return first

    @classmethod
    def create_all_tables(cls):
        create_all_tables(DBSession.engine)

    @classmethod
    def delete_all_tables(cls, force: bool = False):
        delete_all_tables(DBSession.engine, force)


from fsqlfly.settings import ENGINE

DBSession.init_engine(ENGINE)


def update_default_value(mapper, connection, target):
    if target.is_default:
        connection.execute(
            'update %s set is_default = 0 where id <> %d and is_default = 1' % (mapper.local_table.fullname, target.id))


for _mode in ['after_insert', 'after_update']:
    for _model in [ResourceTemplate, ResourceVersion]:
        event.listen(_model, _mode, update_default_value)
