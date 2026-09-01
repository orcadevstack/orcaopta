"""
Shared helpers for feature engineering.
"""

from typing import Dict


def normalize_feature(value: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0
    return (value - mean) / std
