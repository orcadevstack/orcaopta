import time
from .store import TrackingStore
from .artifacts import ArtifactStore

class Tracker:
    def __init__(self, experiment: str = "default"):
        self.store = TrackingStore(experiment)
        self.artifacts = ArtifactStore(experiment)

    def log_metric(self, name: str, value: float):
        self.store.save_metric(name, value, timestamp=time.time())

    def log_param(self, name: str, value):
        self.store.save_param(name, value)

    def log_artifact(self, file_path: str):
        return self.artifacts.save_artifact(file_path)

    def start_run(self):
        return self.store.start_run()

    def end_run(self):
        return self.store.end_run()
