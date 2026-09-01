"""
RL environment for anomaly response (block, throttle, ignore).
"""

from typing import Dict, Any


class AnomalyEnv:
    """
    State: anomaly score + context
    Actions: 0 = ignore, 1 = throttle, 2 = block
    Reward: fewer anomalies, less impact
    """

    def __init__(self) -> None:
        self.state: Dict[str, float] = {}
        self.last_action: int | None = None

    def reset(self, initial_state: Dict[str, float]) -> Dict[str, float]:
        self.state = initial_state
        self.last_action = None
        return self.state

    def step(self, action: int, next_state: Dict[str, float]) -> tuple[Dict[str, float], float, bool, Dict[str, Any]]:
        self.last_action = action
        self.state = next_state

        anomaly_score = self.state.get("anomaly_score", 0.0)
        reward = -anomaly_score

        done = False
        info: Dict[str, Any] = {}

        return self.state, reward, done, info
