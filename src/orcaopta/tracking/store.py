import json
import os
import time

BASE = "/app/data/tracking"

class TrackingStore:
    def __init__(self, experiment: str):
        self.experiment = experiment
        self.run_id = None
        os.makedirs(f"{BASE}/{experiment}", exist_ok=True)

    def start_run(self):
        self.run_id = str(int(time.time()))
        os.makedirs(f"{BASE}/{self.experiment}/{self.run_id}", exist_ok=True)
        return self.run_id

    def end_run(self):
        self.run_id = None

    def _write(self, filename, data):
        path = f"{BASE}/{self.experiment}/{self.run_id}/{filename}"
        with open(path, "a") as f:
            f.write(json.dumps(data) + "\n")

    def save_metric(self, name, value, timestamp):
        self._write("metrics.jsonl", {"name": name, "value": value, "ts": timestamp})

    def save_param(self, name, value):
        self._write("params.jsonl", {"name": name, "value": value})
