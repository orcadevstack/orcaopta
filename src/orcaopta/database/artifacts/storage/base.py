class StorageBackend:
    def save(self, src: str, dst: str):
        raise NotImplementedError

    def load(self, path: str) -> bytes:
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        raise NotImplementedError

    def delete(self, path: str):
        raise NotImplementedError
