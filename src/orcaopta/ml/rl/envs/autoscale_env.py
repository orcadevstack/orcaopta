"""
RL environment for autoscaling decisions.
"""

from typing import Dict, Any


class AutoscaleEnv:
    """
    Minimal RL environment skeleton.

    State: metrics from logs
    Actions: 0 = hold, 1 = scale_up, 2 = scale_down
    Reward: based on latency + resource usage
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

        latency = self.state.get("latency_ms", 0.0)
        cpu = self.state.get("cpu_percent", 0.0)

        reward = -latency / 1000.0 - cpu / 100.0
        done = False
        info: Dict[str, Any] = {}

        return self.state, reward, done, info
