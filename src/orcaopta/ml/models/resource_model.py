"""
Resource optimization model: learns how to balance storage/compute usage.
"""

from typing import Dict


class ResourceModel:
    """
    Placeholder resource optimization model.

    Later you can plug in:
    - regression models
    - RL policies
    """

    def suggest(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Suggest target values for resources, e.g. replication factor, pool size.
        """
        usage = features.get("storage_usage_gb", 0.0)
        replication_factor = features.get("replication_factor", 3.0)

        suggestion: Dict[str, float] = {}

        if usage > 0 and usage > 0.8 * 1000:  # example: 80% of 1TB
            suggestion["increase_pool_capacity"] = 1.0
        else:
            suggestion["increase_pool_capacity"] = 0.0

        suggestion["replication_factor_target"] = replication_factor

        return suggestion
