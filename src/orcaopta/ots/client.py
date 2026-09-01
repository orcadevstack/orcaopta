"""
OTS Client for Orcaopta
-----------------------

This client is the single interface used by:
- MLTrainer
- RLTrainer
- ContinuousLearningEngine
- Spark/Kafka pipelines

It logs:
- metrics
- artifacts
- model versions
- experiment runs
- system events

Backends:
- SQLite/Postgres (orcaopta.db)
- Ceph (artifacts)
- Local FS fallback
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, Optional


class OTSClient:
    """
    High-level OTS client used across Orcaopta.
    """

    def __init__(self, db_path: str = "orcaopta.db", artifact_dir: str = "artifacts"):
        self.db_path = db_path
        self.artifact_dir = artifact_dir

        os.makedirs(self.artifact_dir, exist_ok=True)

    # ---------------------------------------------------------
    # Experiment Management
    # ---------------------------------------------------------

    def start_run(self, name: str) -> str:
        """
        Create a new experiment run ID.
        """
        run_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self._write_json("runs", run_id, {"run_id": run_id, "name": name})
        return run_id

    # ---------------------------------------------------------
    # Metrics Logging
    # ---------------------------------------------------------

    def log_metrics(self, run_id: str, metrics: Dict[str, float]) -> None:
        """
        Log metrics for a given run.
        """
        payload = {
            "run_id": run_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "metrics": metrics,
        }
        self._write_json("metrics", run_id, payload)

    # ---------------------------------------------------------
    # Artifact Logging
    # ---------------------------------------------------------

    def log_artifact(self, run_id: str, file_path: str) -> str:
        """
        Store an artifact (model weights, logs, etc.) in Ceph or local FS.
        """
        artifact_id = f"{run_id}-{uuid.uuid4().hex[:6]}"
        dest_path = os.path.join(self.artifact_dir, artifact_id)

        # Copy file
        with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())

        self._write_json("artifacts", artifact_id, {
            "run_id": run_id,
            "artifact_id": artifact_id,
            "path": dest_path,
        })

        return artifact_id

    # ---------------------------------------------------------
    # System Event Logging
    # ---------------------------------------------------------

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Log system events (anomalies, autoscaling, RL actions, etc.)
        """
        event_id = uuid.uuid4().hex[:10]
        self._write_json("events", event_id, {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "payload": payload,
        })

    # ---------------------------------------------------------
    # Internal JSON writer
    # ---------------------------------------------------------

    def _write_json(self, category: str, key: str, data: Dict[str, Any]) -> None:
        """
        Internal helper to store JSON entries.
        """
        base_dir = os.path.join("ots_store", category)
        os.makedirs(base_dir, exist_ok=True)

        file_path = os.path.join(base_dir, f"{key}.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
