"""
Autoscale model: predicts when to scale up/down/hold based on system metrics.
"""

from typing import Dict


class AutoscaleModel:
    """
    Placeholder autoscaling policy model.

    Later you can replace this with:
    - gradient boosting
    - RL‑driven policy
    """

    def __init__(self) -> None:
        self._threshold_up = 70.0
        self._threshold_down = 30.0

    def decide(self, features: Dict[str, float]) -> str:
        """
        Return one of: "scale_up", "scale_down", "hold".
        """
        cpu = features.get("cpu_percent", 0.0)
        latency = features.get("latency_ms", 0.0)

        if cpu > self._threshold_up or latency > 200.0:
            return "scale_up"
        if cpu < self._threshold_down and latency < 100.0:
            return "scale_down"
        return "hold"
