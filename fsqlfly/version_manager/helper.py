from typing import Union, List

from fsqlfly.common import PageModel, DBRes, SchemaContent, NameFilter
from fsqlfly.db_helper import SUPPORT_MODELS, DBDao, Connection
from fsqlfly.version_manager.factory import ManagerFactory


class ManagerHelper:
    all_support_key = PageModel.keys()

    @classmethod
    def run(cls, model: str, mode: str, pk: Union[str, int]) -> DBRes:
        if model not in SUPPORT_MODELS:
            return DBRes.api_error(msg='{} not support'.format(model))
        if isinstance(pk, str) and not pk.isnumeric():
            pk = DBDao.name2pk(model, name=pk)
        manager = ManagerFactory.get_manager(model, mode)

        return getattr(manager, mode)(model, pk if isinstance(pk, int) else int(pk))


class SynchronizationHelper:
    @classmethod
    def synchronize(cls, connection: Connection, name_filter: NameFilter) -> List[SchemaContent]:
        pass