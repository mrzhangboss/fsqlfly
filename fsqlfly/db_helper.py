from fsqlfly.db_models import *
import os
import traceback
import yaml
from functools import wraps, partial
from copy import deepcopy
from typing import Callable, Type, Optional, List, Union, Any, TypeVar
from sqlalchemy import and_, event, or_, subquery
from sqlalchemy.engine import Engine
from fsqlfly import settings
from fsqlfly.common import DBRes
from sqlalchemy.orm.session import Session, sessionmaker, query as session_query
from fsqlfly.settings import FSQLFLY_UPLOAD_DIR, FSQLFLY_FLINK_BIN, logger

Query = session_query.Query

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

DBT = TypeVar('DBT', Connection, Connector, SchemaEvent, ResourceName, ResourceTemplate,
              ResourceVersion, FileResource, Functions, Transform, Namespace, TransformSavepoint)


class DBSession:
    engine = None
    _Session = None

    @classmethod
    def init_engine(cls, engine: Engine):
        cls.engine = engine
        cls._Session = sessionmaker(bind=engine)

    @classmethod
    def get_session(cls, *args, **kwargs) -> Session:
        assert cls.engine is not None
        return cls._Session(*args, **kwargs)


def session_add(func: Callable) -> Callable:
    @wraps(func)
    def _add_session(*args, **kwargs):
        session = kwargs['session'] if 'session' in kwargs else DBSession.get_session()
        new_kwargs = {k: v for k, v in kwargs.items() if k != 'session'}
        try:
            res = func(*args, session=session, **new_kwargs)
            session.commit()
            return res
        except Exception as error:
            session.rollback()
            if settings.FSQLFLY_DEBUG:
                raise error
            err = traceback.format_exc()
            return DBRes.sever_error(msg=f'meet {err}')
        finally:
            if 'session' not in kwargs:
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
    def name2pk(cls, model: str, name: str, *args, session: Session, base: Type[DBT], **kwargs) -> int:
        return session.query(base.id).filter(base.name == name).one()[0]

    @classmethod
    def is_null_foreign_key(cls, k: str, v: Any) -> bool:
        return k.endswith('_id') and v == 0

    @classmethod
    @session_add
    @filter_not_support
    def update(cls, model: str, pk: int, obj: dict, *args, session: Session, base: Type[Base], **kwargs) -> DBRes:
        assert session is not None
        first = session.query(base).filter(base.id == pk).first()
        if first is None:
            return DBRes.not_found()

        if first.is_locked and obj.get('is_locked') is False:
            return DBRes.resource_locked()

        for k, v in obj.items():
            if k not in ['id', 'create_at', 'update_at'] and not cls.is_null_foreign_key(k, v):
                setattr(first, k, v)
        return DBRes(data=first.as_dict())

    @classmethod
    @session_add
    @filter_not_support
    def create(cls, model: str, obj: dict, *args, session: Session, base: Type[DBT], **kwargs) -> DBRes:
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
    def get_job_names(cls, *args, session: Session, **kwargs) -> dict:
        res = dict()
        query = session.query(Transform).join(Transform.namespace, isouter=True)
        for q in (and_(Transform.is_daemon.is_(True), Namespace.is_daemon.is_(True)),
                  and_(Transform.namespace_id.is_(None), Transform.is_daemon.is_(True))):
            for x in query.filter(q).all():
                res["{}_{}".format(x.id, x.name)] = x

        return res

    @classmethod
    @session_add
    def get_require_name(cls, *args, session: Session, **kwargs) -> DBRes:
        query = session.query(ResourceVersion.full_name).join(ResourceVersion.connection).join(
            ResourceVersion.resource_name)
        version_data = [x[0] for x in
                        query.filter(and_(Connection.is_active == True, ResourceName.is_active == True)).all()]

        v_query = session.query(ResourceVersion).join(ResourceVersion.connection).join(
            ResourceVersion.resource_name)
        default_version_data = list(x.template.full_name for x in v_query.filter(
            and_(Connection.is_active == True, ResourceName.is_active == True,
                 ResourceVersion.is_default == True)).all())
        t_query = session.query(ResourceTemplate).join(ResourceTemplate.connection).join(
            ResourceTemplate.resource_name)
        resource_data = list(x.resource_name.full_name for x in t_query.filter(
            and_(Connection.is_active == True,
                 ResourceName.is_active == True,
                 ResourceTemplate.is_default == True)).all())

        hive_data = [x[0] for x in session.query(Connection.name).filter(Connection.is_active == True,
                                                                         Connection.type == 'hive').all()]

        return DBRes(data=hive_data + version_data + default_version_data + resource_data)

    @classmethod
    def is_hive_table(cls, full_name: str) -> bool:
        return '.' not in full_name

    @classmethod
    @session_add
    def get_require_table(cls, require: str, *args, session: Session, **kwargs) -> List[dict]:
        names = set()
        res = []
        for full_name in require.split(','):
            if cls.is_hive_table(full_name):
                continue
            version = session.query(ResourceVersion).filter(ResourceVersion.full_name == full_name).first()
            if version is None:
                version = session.query(ResourceVersion).join(ResourceVersion.template).filter(
                    and_(ResourceTemplate.full_name == full_name,
                         ResourceVersion.is_default == True)).first()
                if version is None:
                    version = session.query(ResourceVersion).join(ResourceVersion.template).join(
                        ResourceVersion.resource_name).filter(and_(ResourceName.full_name == full_name,
                                                                   ResourceTemplate.is_default == True,
                                                                   ResourceVersion.is_default == True)).first()

            assert version, "Not Found {} in database, try use full name".format(full_name)
            cache = version.generate_version_cache()
            r_name = version.resource_name
            t_name = version.template
            cache['type'] = version.template.type.code
            for name in [r_name.name, r_name.full_name, t_name.full_name]:
                if name not in names:
                    cache['name'] = name.replace('.', '__')
                    names.add(name)
                    break
            if 'name' in cache:
                res.append(cache)
            full_name_cache = deepcopy(cache)
            full_name_cache['name'] = version.full_name.replace('.', '__')
            res.append(full_name_cache)

        return res

    @classmethod
    @session_add
    def get_require_catalog(cls, require: str, *args, session: Session, **kwargs) -> List[dict]:
        names = set()
        res = []
        for full_name in require.split(','):
            if cls.is_hive_table(full_name):
                hive = session.query(Connection).filter(Connection.is_active == True,
                                                        Connection.type == 'hive',
                                                        Connection.name == full_name).one()
                conn = hive.get_connection_connector()
                conn['name'] = hive.name
                if hive.name not in names:
                    res.append(conn)
                    names.add(hive.name)

        return res

    @classmethod
    @session_add
    def get_require_functions(cls, *args, session: Session, **kwargs) -> List[dict]:
        res = []
        for f in session.query(Functions).filter(Functions.is_active == True).all():
            fc = {
                'name': f.name,
                'from': f.function_from,
                'class': f.class_name
            }
            if f.constructor_config.strip():
                fc['constructor'] = yaml.load(f.constructor_config, yaml.FullLoader)
            res.append(fc)
        return res

    @classmethod
    @session_add
    def get_require_jar(cls, *args, session: Session, **kwargs) -> List[str]:
        res = []
        for f in session.query(Functions).filter(Functions.is_active == True).all():
            r_p = os.path.join(FSQLFLY_UPLOAD_DIR, f.resource.real_path[1:])
            res.append(r_p)

        out = []
        for x in set(res):
            out.extend(['-j', x])
        return out

    @classmethod
    def one(cls, *args, session: Session,
            base: Type[DBT], pk: int,
            **kwargs) -> DBT:
        return session.query(base).filter(base.id == pk).one()

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
    def _clean(cls, obj: DBT, session: Session, base: Type[DBT]):
        back = obj.as_dict()
        session.delete(obj)
        session.commit()
        session.add(base(**back))
        session.commit()

    @classmethod
    @session_add
    @filter_not_support
    def clean(cls, model: str, pk: int, *args, session: Session, base: Type[DBT], **kwargs) -> DBRes:
        obj = session.query(base).get(pk)
        if isinstance(obj, Connector):
            back = obj.as_dict()
            source, target = obj.source, obj.target
            session.delete(obj)
            session.commit()
            cls._clean(source, session, Connection)
            cls._clean(target, session, Connection)
            session.add(Connector(**back))
        else:
            if isinstance(obj, Connection):
                s_names = [x[0] for x in
                           session.query(Connector.name).join(Connector.source).filter(Connection.id == pk).all()]
                t_names = [x[0] for x in
                           session.query(Connector.name).join(Connector.target).filter(Connection.id == pk).all()]
                msg = "please clean connector source: {} target: {}".format(','.join(s_names), ','.join(t_names))
                if s_names or t_names:
                    return DBRes.api_error(msg)
            cls._clean(obj, session, base)
        return DBRes()

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
    def save(cls, obj: Base, *args, session: Session, **kwargs) -> Base:
        session.add(obj)
        session.commit()
        return obj

    @classmethod
    def upsert_schema_event(cls, obj: SchemaEvent, *args, session: Session, **kwargs) -> (SchemaEvent, bool):
        inserted = True
        query = session.query(SchemaEvent).filter(and_(SchemaEvent.database == obj.database,
                                                       SchemaEvent.name == obj.name,
                                                       SchemaEvent.connection_id == obj.connection_id))
        res = first = query.order_by(SchemaEvent.version.desc()).first()
        if first:
            if first.fields != obj.fields or first.primary_key != obj.primary_key or obj.partitionable != obj.partitionable:
                obj.version = first.version + 1
                obj.father = first
                res = obj
            else:
                inserted = False
                res.info = obj.info
                res.comment = obj.comment
        else:
            res = obj
        session.add(res)
        session.commit()
        return res, inserted

    @classmethod
    def upsert_resource_name(cls, obj: ResourceName, *args, session: Session, **kwargs) -> (ResourceName, bool):
        inserted = False
        query = session.query(ResourceName).filter(and_(ResourceName.full_name == obj.full_name,
                                                        ResourceName.connection_id == obj.connection_id))
        res = first = query.first()
        if first:
            res.latest_schema_id = obj.latest_schema_id
            res.info = obj.info
            res.is_latest = True
            res.schema_version_id = obj.schema_version_id
        else:
            inserted = True
            res = obj
        session.add(res)
        session.commit()
        return res, inserted

    @classmethod
    def upsert_resource_template(cls, obj: ResourceTemplate, *args,
                                 session: Session, **kwargs) -> (ResourceTemplate, bool):
        query = session.query(ResourceTemplate).filter(and_(ResourceTemplate.name == obj.name,
                                                            ResourceTemplate.connection_id == obj.connection_id,
                                                            ResourceTemplate.resource_name_id == obj.resource_name_id))
        inserted = False
        res = first = query.first()
        if first:
            res.config = obj.config
            res.info = obj.info
            res.is_system = obj.is_system
            res.is_default = obj.is_default
            res.full_name = obj.full_name
            res.schema_version_id = obj.schema_version_id
        else:
            inserted = True
            res = obj
        session.add(res)
        session.commit()
        return res, inserted

    @classmethod
    def upsert_resource_version(cls, obj: ResourceVersion, *args, session: Session,
                                **kwargs) -> (ResourceVersion, bool):
        max_version_obj = session.query(ResourceVersion.version).filter(
            ResourceVersion.template_id == obj.template_id).order_by(ResourceVersion.version.desc()).first()
        max_version = max_version_obj[0] if max_version_obj else 0
        query = session.query(ResourceVersion).filter(and_(ResourceVersion.name == obj.name,
                                                           ResourceVersion.template_id == obj.template_id))
        inserted = True
        res = first = query.order_by(ResourceVersion.version.desc()).first()
        if first:
            if first.config != obj.config:
                res.version = max_version + 1
            res.config = obj.config
            res.cache = obj.cache
            res.info = obj.info
            res.cache = obj.cache
            res.schema_version_id = obj.schema_version_id
            inserted = False
        else:
            res = obj
            res.version = max_version + 1
        session.add(res)
        session.commit()
        return res, inserted

    @classmethod
    def upsert_transform(cls, obj: Transform, *args, session: Session,
                         **kwargs) -> (Transform, bool):
        query = session.query(Transform).filter(Transform.name == obj.name)
        inserted = True
        res = first = query.first()
        if first:
            first.sql = obj.sql
            first.connector_id = obj.connector_id
            first.info = obj.info
            first.require = obj.require
            first.yaml = obj.yaml
            first.namespace_id = obj.namespace_id
            first.is_daemon = obj.is_daemon
            inserted = False
        else:
            res = obj
        session.add(res)
        session.commit()
        return res, inserted

    @classmethod
    def create_all_tables(cls):
        create_all_tables(DBSession.engine)

    @classmethod
    def delete_all_tables(cls, force: bool = False):
        delete_all_tables(DBSession.engine, force)


from fsqlfly.settings import ENGINE

DBSession.init_engine(ENGINE)


def update_default_value(mapper, connection, target, father_name):
    if target.is_default:
        father_id = getattr(target, father_name)
        father_id = int(father_id) if isinstance(father_id, str) else father_id
        connection.execute(
            'update %s set is_default = 0 where id <> %d and is_default = 1 and %s = %d' % (
                mapper.local_table.fullname, target.id, father_name, father_id))


for _mode in ['after_insert', 'after_update']:
    for _model, f_n in zip([ResourceTemplate, ResourceVersion], ['resource_name_id', 'template_id']):
        event.listen(_model, _mode, partial(update_default_value, father_name=f_n))
