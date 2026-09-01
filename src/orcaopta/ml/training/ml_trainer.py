"""
ML training orchestration: trains anomaly/autoscale/resource models from log‑derived features.
"""

from typing import List, Dict
from orcaopta.ml.models.anomaly_model import AnomalyModel
from orcaopta.ml.models.autoscale_model import AutoscaleModel
from orcaopta.ml.models.resource_model import ResourceModel


class MLTrainer:
    def __init__(self) -> None:
        self.anomaly_model = AnomalyModel()
        self.autoscale_model = AutoscaleModel()
        self.resource_model = ResourceModel()

    def train_anomaly(self, feature_list: List[Dict[str, float]]) -> None:
        self.anomaly_model.train(feature_list)

    def run_autoscale_decision(self, features: Dict[str, float]) -> str:
        return self.autoscale_model.decide(features)

    def run_resource_suggestion(self, features: Dict[str, float]) -> Dict[str, float]:
        return self.resource_model.suggest(features)
