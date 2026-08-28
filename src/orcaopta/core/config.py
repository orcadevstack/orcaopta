import yaml
import os

CONFIG_PATH = os.getenv("ORCAOPTA_CONFIG", "configs/orcaopta.yaml")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
