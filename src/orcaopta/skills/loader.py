import importlib
from .registry import SkillRegistry

registry = SkillRegistry()

def load_skill(path: str, name: str):
    module = importlib.import_module(path)
    cls = getattr(module, name)
    registry.register(name, cls)
    return cls()
