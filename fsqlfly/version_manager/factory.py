from fsqlfly.version_manager import BaseVersionManager


class ManagerFactory:

    @classmethod
    def get_manager_factory(cls, model: str, mode, pk: str) -> BaseVersionManager:
        raise NotImplementedError("current not support {} - {} ".format(model, mode))


class ResourceGeneratorFactor:
    pass


class SynchronizationFactory:
    pass
