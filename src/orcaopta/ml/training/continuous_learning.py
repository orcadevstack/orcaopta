"""
Continuous learning loop: ties logs → features → ML → RL → improved decisions.
"""

from typing import List, Dict, Any

from orcaopta.ml.data.log_preprocessor import preprocess_log
from orcaopta.ml.data.feature_builder import build_features

from orcaopta.ml.training.ml_trainer import MLTrainer
from orcaopta.ml.training.rl_trainer import RLTrainer

from orcaopta.ots.client import OTSClient


class ContinuousLearningEngine:
    """
    High‑level orchestrator for self‑learning behavior.
    This engine:
    - receives logs from Spark/Kafka
    - preprocesses logs
    - builds ML features
    - trains ML anomaly model
    - trains RL agents
    - logs metrics + events to OTS
    """

    def __init__(self) -> None:
        # ML + RL trainers
        self.ml_trainer = MLTrainer()
        self.rl_trainer = RLTrainer()

        # OTS client
        self.ots = OTSClient()

        # Create a new OTS run for this continuous learning session
        self.run_id = self.ots.start_run("continuous-learning")

    def process_logs(self, raw_logs: List[Dict[str, Any]], config_state: Dict[str, Any]) -> None:
        """
        Ingest logs, build features, train ML, train RL, and log everything to OTS.
        """

        # ---------------------------------------------------------
        # 1. Preprocess logs
        # ---------------------------------------------------------
        cleaned_logs = [preprocess_log(log) for log in raw_logs]

        # ---------------------------------------------------------
        # 2. Build ML features
        # ---------------------------------------------------------
        features_list = [build_features(log, config_state) for log in cleaned_logs]

        # Log each feature set to OTS as metrics
        for features in features_list:
            self.ots.log_metrics(self.run_id, features)

        # ---------------------------------------------------------
        # 3. Train anomaly model
        # ---------------------------------------------------------
        self.ml_trainer.train_anomaly(features_list)

        # Compute anomaly score for the latest log
        latest_features = features_list[-1] if features_list else {}
        anomaly_score = self.ml_trainer.anomaly_model.score(latest_features)

        # Log anomaly score as an OTS event
        self.ots.log_event("anomaly_score", {"score": anomaly_score})

        # ---------------------------------------------------------
        # 4. Run autoscale decision (ML)
        # ---------------------------------------------------------
        autoscale_decision = self.ml_trainer.run_autoscale_decision(latest_features)

        self.ots.log_event("autoscale_decision", {
            "decision": autoscale_decision,
            "features": latest_features
        })

        # ---------------------------------------------------------
        # 5. Run resource optimization (ML)
        # ---------------------------------------------------------
        resource_suggestion = self.ml_trainer.run_resource_suggestion(latest_features)

        self.ots.log_event("resource_suggestion", resource_suggestion)

        # ---------------------------------------------------------
        # 6. Train RL agents (periodic)
        # ---------------------------------------------------------
        self.rl_trainer.train_all()

        self.ots.log_event("rl_training", {
            "status": "completed",
            "autoscale_agent": "ppo",
            "anomaly_agent": "dqn",
            "resource_agent": "ppo"
        })

        # ---------------------------------------------------------
        # 7. Optional: Save anomaly model weights as artifact
        # ---------------------------------------------------------
        # Example: save model weights to file and log to OTS
        # (You can implement saving inside anomaly_model.py)
        #
        # model_path = self.ml_trainer.anomaly_model.save("anomaly_model.pkl")
        # self.ots.log_artifact(self.run_id, model_path)
