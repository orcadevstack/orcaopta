import os

def resolve_path(base_dir: str, artifact_name: str, version: int):
    return os.path.join(base_dir, f"{artifact_name}_v{version}")
