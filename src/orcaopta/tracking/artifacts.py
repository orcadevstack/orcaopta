import os
import shutil

BASE = "/app/data/artifacts"

class ArtifactStore:
    def __init__(self, experiment: str):
        self.experiment = experiment
        os.makedirs(f"{BASE}/{experiment}", exist_ok=True)

    def save_artifact(self, file_path: str):
        dest = f"{BASE}/{self.experiment}/{os.path.basename(file_path)}"
        shutil.copy(file_path, dest)
        return dest
