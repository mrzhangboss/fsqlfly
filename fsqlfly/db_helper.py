from fsqlfly.db_models import *
import traceback
from sqlalchemy.engine import Engine
from functools import wraps
from typing import Callable, Type
from fsqlfly.common import DBRes, RespCode
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


def filter_not_support(func: Callable) -> Callable:
    @wraps(func)
    def _call_(*args, **kwargs):
        model = kwargs['model'] if 'model' in kwargs else args[1]
        if model not in SUPPORT_MODELS:
            return DBRes(code=RespCode.APIFail.code, msg=f'{model} not support')
        base = SUPPORT_MODELS[model]
        session = kwargs['session'] if 'session' in kwargs else DBSession.get_session()
        try:
            res = func(*args, session=session, base=base, **kwargs)
            session.commit()
            return res
        except Exception:
            session.rollback()
            err = traceback.format_exc()
            return DBRes(code=RespCode.APIFail.code, msg=f'{model} meet {err}')
        finally:
            session.close()

    return _call_


class DBDao:
    @classmethod
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
    @filter_not_support
    def create(cls, model: str, obj: dict, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        pass

    @classmethod
    @filter_not_support
    def get(cls, model: str, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        pass

    @classmethod
    @filter_not_support
    def delete(cls, model: str, pk: int, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        pass
