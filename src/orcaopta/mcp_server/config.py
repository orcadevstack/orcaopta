import os


def get_mode() -> str:
    return os.getenv("ORCAOPTA_MODE", "cluster")


def get_config_path() -> str:
    return os.getenv("ORCAOPTA_CONFIG", "/app/configs/orcaopta.yaml")
