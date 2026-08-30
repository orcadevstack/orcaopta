import os

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def file_exists(path: str) -> bool:
    return os.path.isfile(path)

ensure_dir("models/")
