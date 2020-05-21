from typing import Union

from fsqlfly.common import PageModel, DBRes
from fsqlfly.version_manager.factory import ManagerFactory
from fsqlfly.version_manager.dao import Dao


class ManagerHelper:
    all_support_key = PageModel.keys()

    @classmethod
    def run(cls, model: str, mode: str, pk: Union[str, int]) -> DBRes:
        dao = Dao()
        obj = dao.get_by_name_or_id(model, pk)
        if obj:
            manager = ManagerFactory.get_manager(model, mode, obj, dao)
            if manager.is_support():
                return manager.run()
            else:
                msg = "Not support {}:{} in model {} by {} in ManagerHelper".format(obj.name, obj.id, model, mode)
                return DBRes.api_error(msg)
        else:
            return DBRes.api_error("Not found {} in model {}".format(pk, model))


