class BaseVersionManager:
    def is_support(self, pk: str) -> bool:
        raise NotImplementedError

    def run(self, pk: str):
        raise NotImplementedError



class BaseVersionManagerFactory:
    def get_manager(self):
        pass