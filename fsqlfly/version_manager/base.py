from fsqlfly.common import DBRes


class IBaseVersionManager:
    def run(self) -> DBRes:
        raise NotImplementedError

    def is_support(self) -> bool:
        raise NotImplementedError


class BaseVersionManager(IBaseVersionManager):
    def run(self) -> DBRes:
        raise NotImplementedError

    def is_support(self) -> bool:
        return False

    @classmethod
    def not_support_manager(cls):
        return BaseVersionManager()
