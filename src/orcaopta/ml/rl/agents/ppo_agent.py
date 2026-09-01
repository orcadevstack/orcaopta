"""
Placeholder PPO agent skeleton.
"""

from typing import Dict


class PPOAgent:
    """
    High‑level PPO agent interface.

    You can later plug in:
    - stable‑baselines3
    - custom PyTorch implementation
    """

    def __init__(self) -> None:
        self._initialized = True

    def act(self, state: Dict[str, float]) -> int:
        """
        Return an action index given a state.
        For now, just a dummy policy.
        """
        return 0

    def update(self, trajectories) -> None:
        """
        Update policy from collected trajectories.
        """
        pass
