from fsqlfly.db_models import *
from fsqlfly.common import DBRes


class DBDao(object):
    @classmethod
    def update(cls, pk: int, model: str, obj: dict) -> DBRes:
        pass

    @classmethod
    def create(cls, model: str, obj: dict) -> DBRes:
        pass

    @classmethod
    def get(cls, model: str) -> DBRes:
        pass

    @classmethod
    def delete(cls, pk: int, model: str) -> DBRes:
        pass
