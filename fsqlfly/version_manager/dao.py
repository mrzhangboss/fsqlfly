from typing import Optional, Callable, Any, Union
from fsqlfly.db_helper import (Session, DBSession, SchemaEvent, and_, ResourceName, ResourceTemplate, ResourceVersion,
                               Transform, SUPPORT_MODELS, DBT, Connection, Connector)
from fsqlfly.common import DBRes


class BaseDao:
    def __init__(self, session: Optional[Session] = None):
        self._session = session
        self.cache_session = None

    @property
    def session(self) -> Session:
        if self._session:
            return self._session
        if self.cache_session is None:
            self.cache_session = DBSession.get_session()
        return self.cache_session

    def finished(self):
        if self.cache_session:
            self.cache_session.close()


def auto_commit(func: Callable):
    def _real_auto_commit(self: BaseDao, *args, **kwargs) -> Any:
        try:
            res = func(self, *args, **kwargs)
            self.session.commit()
            return res
        except Exception as err:
            self.session.rollback()
            raise err

    return _real_auto_commit


class Dao(BaseDao):
    @classmethod
    def schema_is_equal(cls, a: SchemaEvent, b: SchemaEvent) -> bool:
        return a.fields != b.fields or a.primary_key != b.primary_key or b.partitionable != b.partitionable

    def upsert_schema_event(self, obj: SchemaEvent) -> (SchemaEvent, bool):
        session = self.session
        inserted = True
        query = session.query(SchemaEvent).filter(and_(SchemaEvent.database == obj.database,
                                                       SchemaEvent.name == obj.name,
                                                       SchemaEvent.connection_id == obj.connection_id))
        res = first = query.order_by(SchemaEvent.version.desc()).first()
        if first:
            if self.schema_is_equal(first, obj):
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

    def upsert_resource_name(self, obj: ResourceName) -> (ResourceName, bool):
        session = self.session
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

    def upsert_resource_template(self, obj: ResourceTemplate) -> (ResourceTemplate, bool):
        session = self.session
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

    def upsert_resource_version(self, obj: ResourceVersion) -> (ResourceVersion, bool):
        session = self.session
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

    def upsert_transform(self, obj: Transform) -> (Transform, bool):
        session = self.session
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

    def name2pk(self, model: str, name: str) -> int:
        base = SUPPORT_MODELS[model]
        return self.session.query(base.id).filter(base.name == name).one()[0]

    def get_by_name_or_id(self, model: str, pk: Union[str, int]) -> Optional[DBT]:
        base = SUPPORT_MODELS[model]
        query = self.session.query(base)
        if isinstance(pk, str) and not pk.isdigit():
            query = query.filter(base.name == pk)
        else:
            query = query.filter(base.id == pk)
        return query.first()

    @auto_commit
    def save(self, obj: DBT) -> DBT:
        self.session.add(obj)
        return obj

    @auto_commit
    def clean_connection(self, obj: Connection) -> DBRes:
        num = 0
        for x in self.session.query(ResourceName).join(ResourceName.connection).filter(Connection.id == obj.id).all():
            self.session.delete(x)
            num += 1
        msg = 'clean {} resource name'.format(num)
        return DBRes(msg=msg)

    @auto_commit
    def clean_connector(self, obj: Connector) -> DBRes:
        num = 0
        for x in self.session.query(Transform).join(Transform.connector).filter(Connector.id == obj.id).all():
            self.session.delete(x)
            num += 1
        msg = 'clean {} transform'.format(num)
        return DBRes(msg=msg)

    def get_default_version(self, database: str, table: str, connection_id: int,
                            template_name: str) -> Optional[ResourceVersion]:
        query = self.session.query(ResourceVersion).join(ResourceVersion.connection).join(
            ResourceVersion.resource_name).join(ResourceVersion.template)
        return query.filter(ResourceName.database == database, ResourceName.name == table,
                            ResourceTemplate.name == template_name,
                            Connection.id == connection_id).first()

    def get_default_sink_version(self, database: str, table: str, connection_id: int) -> Optional[ResourceVersion]:
        return self.get_default_version(database, table, connection_id, 'sink')

    def get_default_source_version(self, database: str, table: str, connection_id: int) -> Optional[ResourceVersion]:
        return self.get_default_version(database, table, connection_id, 'source')
