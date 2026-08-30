import yaml
from pathlib import Path
from functools import lru_cache

from orcaopta.utils.tracing import setup_tracing
tracer = setup_tracing()



@lru_cache(maxsize=1)
def load_config(path: str | Path = "orcaopta.yaml") -> dict:
    """
    Load Orcaopta configuration from orcaopta.yaml.
    Cached for performance and consistency across the platform.

    Returns:
        dict: Parsed configuration dictionary.
    """
    with tracer.start_as_current_span("config-load") as span:
        path = Path(path)
        span.set_attribute("config_path", str(path))

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f)

            span.set_attribute("status", "loaded")
            return config

        except Exception as e:
            span.set_attribute("status", "error")
            raise RuntimeError(f"Failed to load configuration: {e}")



def get_api_config():
    return load_config().get("api", {})

def get_database_config():
    return load_config().get("database", {})

def get_model_config():
    return load_config().get("models", {})

def get_data_config():
    return load_config().get("data", {})

def get_cloud_storage_config():
    return load_config().get("cloud_storage", {})

def get_queue_config():
    return load_config().get("queue", {})

def get_ai_config():
    return load_config().get("ai", {})

def get_autoscaling_config():
    return load_config().get("autoscaling", {})

def get_security_config():
    return load_config().get("security", {})

def get_logging_config():
    return load_config().get("logging", {})
