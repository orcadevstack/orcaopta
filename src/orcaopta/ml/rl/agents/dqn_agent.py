"""
Placeholder DQN agent skeleton.
"""

from typing import Dict


class DQNAgent:
    """
    High‑level DQN agent interface.
    """

    def __init__(self) -> None:
        self._initialized = True

    def act(self, state: Dict[str, float]) -> int:
        """
        Return an action index given a state.
        """
        return 0

    def update(self, batch) -> None:
        """
        Update Q‑network from experience batch.
        """
        pass
