import time
from typing import Any, Dict, List, Optional


class SupervisorState:
    """
    Central state manager for the Orcaopta Supervisor.
    Tracks autoscale decisions, healing actions, GPU/CPU/ML/RL signals,
    cloud graph state, cooldown timers, and event history.
    """

    def __init__(self):
        # =========================
        # Core counters
        # =========================
        self.failures_detected: int = 0
        self.healings_performed: int = 0

        # =========================
        # Histories
        # =========================
        self.healing_history: List[Dict[str, Any]] = []
        self.event_history: List[Dict[str, Any]] = []
        self.autoscale_history: List[Dict[str, Any]] = []
        self.detection_history: List[Dict[str, Any]] = []

        # =========================
        # GPU / CPU / ML / RL signal history
        # =========================
        self.gpu_history: List[Dict[str, Any]] = []
        self.cpu_history: List[Dict[str, Any]] = []
        self.ml_anomaly_history: List[Dict[str, Any]] = []
        self.ml_autoscale_history: List[Dict[str, Any]] = []
        self.rl_history: List[Dict[str, Any]] = []

        # =========================
        # Cloud graph state
        # =========================
        self.cloud_graph_snapshots: List[Dict[str, Any]] = []

        # =========================
        # Autoscale engine state
        # =========================
        self.last_autoscale_decision: Optional[str] = None
        self.last_autoscale_time: float = 0.0
        self.cooldown_seconds: int = 60  # default, overridden by config

        # =========================
        # Supervisor uptime
        # =========================
        self.start_time: float = time.time()

        # =========================
        # Prometheus snapshot cache
        # =========================
        self.latest_metrics_snapshot: Dict[str, Any] = {}

    # ============================================================
    # State update helpers
    # ============================================================

    def record_detection(self, snapshot: Dict[str, Any]):
        """Store a detection snapshot."""
        self.detection_history.append(snapshot)

        # Track specific components
        if "gpu" in snapshot:
            self.gpu_history.append(snapshot["gpu"])
        if "cpu" in snapshot:
            self.cpu_history.append(snapshot["cpu"])
        if "ml_anomaly" in snapshot:
            self.ml_anomaly_history.append(snapshot["ml_anomaly"])
        if "ml_autoscale" in snapshot:
            self.ml_autoscale_history.append(snapshot["ml_autoscale"])
        if "rl" in snapshot:
            self.rl_history.append(snapshot["rl"])
        if "cloud_graph" in snapshot:
            self.cloud_graph_snapshots.append(snapshot["cloud_graph"])

    def record_healing(self, healing_result: Dict[str, Any]):
        """Store a healing action."""
        self.healing_history.append(healing_result)
        self.healings_performed += 1

    def record_event(self, event: Dict[str, Any]):
        """Store a generic event."""
        self.event_history.append(event)

    def record_autoscale(self, decision: str, reason: str):
        """Store autoscale decisions."""
        entry = {
            "decision": decision,
            "reason": reason,
            "timestamp": time.time(),
        }
        self.autoscale_history.append(entry)
        self.last_autoscale_decision = decision
        self.last_autoscale_time = time.time()

    def update_metrics_snapshot(self, snapshot: Dict[str, Any]):
        """Store latest Prometheus metrics snapshot."""
        self.latest_metrics_snapshot = snapshot

    # ============================================================
    # Utility
    # ============================================================

    def uptime(self) -> float:
        """Return supervisor uptime in seconds."""
        return time.time() - self.start_time

    def in_cooldown(self) -> bool:
        """Check if autoscale cooldown is active."""
        return (time.time() - self.last_autoscale_time) < self.cooldown_seconds
