from fsqlfly.version_manager import BaseVersionManager


class ManagerFactory:

    @classmethod
    def get_manager_factory(cls, model: str, mode) -> BaseVersionManager:
        raise NotImplementedError("current not support {} - {} ".format(model, mode))
