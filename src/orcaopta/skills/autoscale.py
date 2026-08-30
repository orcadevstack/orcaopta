from .base import Skill

class AutoscaleSkill(Skill):
    name = "autoscale"
    description = "Automatically scale workloads based on metrics."

    def execute(self, cpu_usage: float, threshold: float = 0.8):
        if cpu_usage > threshold:
            return {"action": "scale_up", "reason": "High CPU usage"}
        else:
            return {"action": "no_change", "reason": "CPU normal"}
