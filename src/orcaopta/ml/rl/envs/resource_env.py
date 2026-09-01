"""
RL environment for storage/compute resource tuning.
"""

from typing import Dict, Any


class ResourceEnv:
    """
    State: storage usage, replication, latency
    Actions: 0 = no change, 1 = increase capacity, 2 = decrease capacity
    Reward: lower latency, balanced usage
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
        usage = self.state.get("storage_usage_gb", 0.0)

        reward = -latency / 1000.0 - usage / 10000.0
        done = False
        info: Dict[str, Any] = {}

        return self.state, reward, done, info
