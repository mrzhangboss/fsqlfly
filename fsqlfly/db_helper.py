from fsqlfly.db_models import *
import traceback
from sqlalchemy import and_, event
from sqlalchemy.engine import Engine
from functools import wraps
from typing import Callable, Type, Optional, List, Union
from fsqlfly import settings
from fsqlfly.common import DBRes
from sqlalchemy.orm.session import Session, sessionmaker

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
    @session_add
    @filter_not_support
    def get(cls, model: str, *args, session: Session, base: Type[Base], filter_: Optional[dict] = None,
            **kwargs) -> DBRes:
        query = session.query(base)
        if filter_:
            kvs = [getattr(base, k) == v for k, v in filter_.items()]
            if len(kvs) > 1:
                query = query.filter(and_(*kvs))
            else:
                query = query.filter(kvs[0])
        return DBRes(data=[x.as_dict() for x in query.all()])

    @classmethod
    @session_add
    @filter_not_support
    def delete(cls, model: str, pk: int, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        if settings.FSQLFLY_SAVE_MODE_DISABLE:
            session.query(base).filter(base.id == pk).delete()
            return DBRes(data=pk)
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
    def create_all_tables(cls):
        create_all_tables(DBSession.engine)

    @classmethod
    def delete_all_tables(cls, force: bool = False):
        delete_all_tables(DBSession.engine, force)


from fsqlfly.settings import ENGINE

DBSession.init_engine(ENGINE)


def update_default_value(mapper, connection, target):
    if target.is_default:
        connection.execute('update %s set is_default = 0 where id <> %d and is_default = 1' % (mapper.local_table.fullname, target.id))


for mode in ['after_insert', 'after_update']:
    for model in [ResourceTemplate, ResourceVersion]:
        event.listen(model, mode, update_default_value)
