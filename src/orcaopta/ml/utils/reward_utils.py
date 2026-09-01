"""
Reward utilities for RL environments.
"""

from typing import Dict


def compute_latency_reward(state: Dict[str, float]) -> float:
    latency = state.get("latency_ms", 0.0)
    return -latency / 1000.0
