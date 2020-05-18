from abc import ABC
from typing import Any
from fsqlfly.db_helper import DBSession


class BaseDao:
    def __init__(self):
        self.session = DBSession.get_session()

    def finished(self):
        self.session.close()

    def _run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def run(self, *args, **kwargs) -> Any:
        try:
            res = self._run(*args, **kwargs)
            self.session.commit()
            return res
        except Exception as err:
            self.session.rollback()
            raise err


class Dao(BaseDao, ABC):
    pass
