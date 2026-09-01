import shutil
import os

class LocalStorage:
    def save(self, src: str, dst: str):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)

    def exists(self, path: str):
        return os.path.exists(path)

    def delete(self, path: str):
        if os.path.exists(path):
            os.remove(path)
