"""
Build RL state from logs + config.
"""

from typing import Dict, Any


def build_state_from_features(features: Dict[str, float]) -> Dict[str, float]:
    """
    Convert ML features into an RL state representation.
    """
    return dict(features)
