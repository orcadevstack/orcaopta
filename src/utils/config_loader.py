import yaml
import json

def load_yaml(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)

cfg = load_yaml("configs/api-config.yaml")
