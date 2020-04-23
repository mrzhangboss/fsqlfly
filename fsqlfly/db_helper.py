from fsqlfly.db_models import *
from functools import wraps
from typing import Callable, Type
from fsqlfly.common import DBRes, RespCode

ALL_SUPPORT_MODELS = {
    'connection': Connection
}


class SupportModel:
    def __contains__(self, item):
        return item not in ALL_SUPPORT_MODELS

    def __call__(self, item) -> Type[Base]:
        return ALL_SUPPORT_MODELS[item]


SUPPORT_MODELS = SupportModel()


def filter_not_support(func: Callable) -> Callable:
    @wraps(func)
    def _call_(*args, **kwargs):
        model = kwargs['model'] if 'model' in kwargs else args[1]
        if model not in SUPPORT_MODELS:
            return DBRes(code=RespCode.APIFail.code, msg=f'{model} not support')

        return func(*args, **kwargs)

    return _call_


class DBDao(object):
    @classmethod
    @filter_not_support
    def update(cls, model: str, pk: int, obj: dict) -> DBRes:
        print(obj)

    @classmethod
    @filter_not_support
    def create(cls, model: str, obj: dict) -> DBRes:
        pass

    @classmethod
    @filter_not_support
    def get(cls, model: str) -> DBRes:
        pass

    @classmethod
    @filter_not_support
    def delete(cls, model: str, pk: int) -> DBRes:
        pass
