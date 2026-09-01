"""
Anomaly detection model: learns normal vs abnormal behavior from logs.
"""

from typing import List, Dict
import numpy as np


class AnomalyModel:
    """
    Simple placeholder anomaly model.

    Replace with:
    - IsolationForest
    - Autoencoder
    - LSTM‑based anomaly detector
    """

    def __init__(self) -> None:
        self._trained = False
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    def train(self, feature_list: List[Dict[str, float]]) -> None:
        if not feature_list:
            return

        X = np.array([[v for v in f.values()] for f in feature_list], dtype=float)
        self._mean = X.mean(axis=0)
        self._std = X.std(axis=0) + 1e-6
        self._trained = True

    def score(self, features: Dict[str, float]) -> float:
        """
        Return an anomaly score: higher = more abnormal.
        """
        if not self._trained or self._mean is None or self._std is None:
            return 0.0

        x = np.array(list(features.values()), dtype=float)
        z = (x - self._mean) / self._std
        return float(np.linalg.norm(z))
