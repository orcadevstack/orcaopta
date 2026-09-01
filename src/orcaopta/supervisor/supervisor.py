import asyncio
import logging
import shutil
import subprocess
import json
import time
from typing import Optional, Dict, Any

from orcaopta.utils.device import DEVICE
from orcaopta.spark.spark_worker import SparkWorker
from orcaopta.mcp.worker import MCPWorker
from orcaopta.node.config import NodeConfig
from orcaopta.autoscale.decentralized import DecentralizedAutoscaler

logger = logging.getLogger("orcaopta.supervisor")

config = NodeConfig()
mcp = MCPWorker()
spark = SparkWorker()
autoscaler = DecentralizedAutoscaler()

_last_scale_time: float = 0
_last_decision: Optional[str] = None
_supervisor_service: Optional["SupervisorService"] = None


# ============================================================
# HEALTH / METRICS HELPERS
# ============================================================

def ceph_health() -> Dict[str, Any]:
    if not shutil.which("ceph"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["ceph", "health", "-f", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def k8s_health() -> Dict[str, Any]:
    if not shutil.which("kubectl"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# GPU / NVIDIA-SMI (MULTI-GPU)
# ============================================================

def nvidia_smi_metrics_multi() -> Dict[int, Dict[str, Any]]:
    """
    Collect per-GPU utilization, temperature, and power using nvidia-smi.
    Returns: {index: {util_gpu, util_mem, temperature, power}}
    """
    if shutil.which("nvidia-smi") is None:
        return {}

    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,utilization.gpu,utilization.memory,temperature.gpu,power.draw",
                "--format=csv,noheader,nounits",
            ],
            encoding="utf-8",
        )

        metrics: Dict[int, Dict[str, Any]] = {}
        for line in out.strip().splitlines():
            idx_str, util_gpu_str, util_mem_str, temp_str, power_str = [
                x.strip() for x in line.split(",")
            ]
            idx = int(idx_str)
            metrics[idx] = {
                "util_gpu": int(util_gpu_str),
                "util_mem": int(util_mem_str),
                "temperature": int(temp_str),
                "power": int(power_str),
            }

        return metrics

    except Exception as e:
        logger.warning(f"[GPU] nvidia-smi multi-GPU failed: {e}")
        return {}


def gpu_status_multi() -> Dict[int, Dict[str, Any]]:
    """
    Return per-GPU status keyed by GPU index.
    Includes CUDA memory stats + nvidia-smi metrics when available.
    """
    result: Dict[int, Dict[str, Any]] = {}

    if DEVICE != "cuda":
        result[0] = {"device": "cpu"}
        return result

    try:
        import torch

        smi = nvidia_smi_metrics_multi()
        gpu_count = torch.cuda.device_count()

        for idx in range(gpu_count):
            torch.cuda.set_device(idx)
            props = torch.cuda.get_device_properties(idx)

            entry = {
                "device": "cuda",
                "gpu_index": idx,
                "gpu_name": torch.cuda.get_device_name(idx),
                "memory_total": props.total_memory,
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved(),
            }

            if idx in smi:
                entry.update(smi[idx])

            result[idx] = entry

    except Exception as e:
        logger.warning(f"[GPU] Failed to read multi-GPU status: {e}")
        result[0] = {"device": "cuda", "error": str(e)}

    return result


# ============================================================
# OPTIONAL ML / RL IMPORTS
# ============================================================

try:
    from src.orcaopta.ml import (
        anomaly_detection,
        forecasting,
        resource_optimization,
        autoscaling as ml_autoscaling,
        model_utils,
    )
except Exception:
    anomaly_detection = forecasting = resource_optimization = ml_autoscaling = model_utils = None

try:
    from src.orcaopta.rl import evaluate_rl, agent_ppo
except Exception:
    evaluate_rl = agent_ppo = None


def ml_signals() -> Optional[Dict[str, Any]]:
    if not model_utils:
        return None

    df = model_utils.sample_cluster_metrics()

    return {
        "anomaly": anomaly_detection.predict_anomaly(
            model_utils.load_anomaly(), df
        ).tolist(),
        "forecast": forecasting.predict_future(
            model_utils.load_forecast(), df
        ).tolist(),
        "resource_opt": resource_optimization.optimize_resources(
            model_utils.load_resource_opt(), df
        ).tolist(),
        "autoscale": ml_autoscaling.autoscale_decision(
            model_utils.load_autoscale(), df
        ).tolist(),
    }


def rl_signals() -> Optional[Dict[str, Any]]:
    if not agent_ppo:
        return None

    agent = agent_ppo.load_agent()
    return evaluate_rl.evaluate_agent(agent)


# ============================================================
# INITIAL JOBS / AUTOSCALE
# ============================================================

def run_initial_autoscale() -> None:
    ml_cfg = getattr(config, "ml", {}) or {}
    if not ml_cfg:
        return

    mode = ml_cfg.get("autoscale")
    if mode == "scale_up":
        logger.info("[Supervisor] Initial autoscale decision: SCALE UP")
        autoscaler.decide("scale_up")
    elif mode == "scale_down":
        logger.info("[Supervisor] Initial autoscale decision: SCALE DOWN")
        autoscaler.decide("scale_down")


def run_initial_jobs() -> None:
    try:
        logger.info("[Supervisor] Running initial Spark jobs...")
        spark.run("daily_metrics")
        spark.run_pipeline("cloud_ingestion")

        local_metrics = gpu_status_multi()
        global_metrics = mcp.call("spark_run_job", job_name="cluster_aggregation")

        logger.info(f"[Init] Local metrics: {local_metrics}")
        logger.info(f"[Init] Global metrics: {global_metrics}")
    except Exception as e:
        logger.error(f"[Init] Failed to run initial jobs: {e}")


# ============================================================
# AUTOSCALE POLICY + DECISION
# ============================================================

def get_autoscale_policy() -> Dict[str, Any]:
    cfg = getattr(config, "autoscaling", {}) or {}
    policy = cfg.get("policy", {}) or {}

    return {
        "enabled": cfg.get("enabled", False),
        "min_replicas": cfg.get("min_replicas", 1),
        "max_replicas": cfg.get("max_replicas", 20),
        "cooldown_seconds": cfg.get("cooldown_seconds", 60),
        "gpu_up": policy.get("gpu_utilization_scale_up_threshold", 70),
        "gpu_down": policy.get("gpu_utilization_scale_down_threshold", 30),
        "ml_up": policy.get("ml_autoscale_scale_up_threshold", 0.2),
        "ml_down": policy.get("ml_autoscale_scale_down_threshold", -0.2),
        "hysteresis": policy.get("hysteresis_margin", 0.05),
    }


def decide_autoscale_from_signals(
    gpu_all: Dict[int, Dict[str, Any]],
    ml: Optional[Dict[str, Any]],
    last_decision: Optional[str],
) -> Optional[str]:
    policy = get_autoscale_policy()
    if not policy["enabled"]:
        return None

    gpu_utils = [
        g.get("util_gpu", 0) for g in gpu_all.values() if g.get("device") == "cuda"
    ]
    avg_gpu = sum(gpu_utils) / len(gpu_utils) if gpu_utils else 0

    ml_signal = ml.get("autoscale") if ml else None
    ml_mean = sum(ml_signal) / len(ml_signal) if ml_signal else 0

    decision = None

    if avg_gpu >= policy["gpu_up"]:
        decision = "scale_up"
    elif avg_gpu <= policy["gpu_down"]:
        decision = "scale_down"

    if ml_mean >= policy["ml_up"] + policy["hysteresis"]:
        decision = "scale_up"
    elif ml_mean <= policy["ml_down"] - policy["hysteresis"]:
        decision = "scale_down"

    if decision and last_decision and decision != last_decision:
        # place for more advanced hysteresis if needed
        pass

    return decision


# ============================================================
# OPENSTACK / K8s SCALING STUBS
# ============================================================

def openstack_scale_group(group_name: str, desired: int) -> None:
    logger.warning(f"[OpenStack] Scaling group {group_name} to {desired} instances")
    try:
        subprocess.check_call(
            ["openstack", "stack", "update", group_name, "--parameter", f"desired={desired}"]
        )
    except Exception as e:
        logger.error(f"[OpenStack] Failed to scale group {group_name}: {e}")


def k8s_scale_deployment(namespace: str, name: str, replicas: int) -> None:
    logger.warning(f"[K8s] Scaling deployment {namespace}/{name} to {replicas} replicas")

    if shutil.which("kubectl") is None:
        logger.error("[K8s] kubectl not found")
        return

    try:
        subprocess.check_call(
            ["kubectl", "scale", f"deployment/{name}", f"--replicas={replicas}", "-n", namespace]
        )
    except Exception as e:
        logger.error(f"[K8s] Failed to scale deployment {namespace}/{name}: {e}")


def apply_autoscale_decision(decision: str) -> None:
    global _last_scale_time, _last_decision

    policy = get_autoscale_policy()
    now = time.time()

    if now - _last_scale_time < policy["cooldown_seconds"]:
        logger.info("[Autoscale] Cooldown active, skipping decision")
        return

    logger.warning(f"[Autoscale] Decision: {decision}")
    _last_scale_time = now
    _last_decision = decision

    try:
        autoscaler.decide(decision)
    except Exception as e:
        logger.error(f"[Autoscale] Failed to apply internal decision: {e}")

    desired_replicas = getattr(autoscaler, "current_replicas", policy["min_replicas"])

    if decision == "scale_up":
        desired_replicas += 1
    elif decision == "scale_down":
        desired_replicas = max(policy["min_replicas"], desired_replicas - 1)

    desired_replicas = min(policy["max_replicas"], desired_replicas)

    os_group = getattr(config, "openstack_group", "orcaopta-cluster")
    k8s_ns = getattr(config, "k8s_namespace", "default")
    k8s_dep = getattr(config, "k8s_deployment", "orcaopta-api")

    openstack_scale_group(os_group, desired_replicas)
    k8s_scale_deployment(k8s_ns, k8s_dep, desired_replicas)


# ============================================================
# PROMETHEUS METRICS SNAPSHOT + FORMAT
# ============================================================

def collect_metrics_snapshot() -> Dict[str, Any]:
    gpu = gpu_status_multi()
    ceph = ceph_health()
    k8s = k8s_health()
    ml = ml_signals()
    rl = rl_signals()

    return {
        "gpu": gpu,
        "ceph": ceph,
        "k8s": k8s,
        "ml": ml,
        "rl": rl,
        "device": DEVICE,
        "timestamp": time.time(),
    }


def metrics_to_prometheus(snapshot: Dict[str, Any]) -> str:
    lines = []

    ts = snapshot.get("timestamp", time.time())
    lines.append("# TYPE orcaopta_supervisor_timestamp gauge")
    lines.append(f"orcaopta_supervisor_timestamp {ts}")

    device = snapshot.get("device", "unknown")
    lines.append("# TYPE orcaopta_device_info gauge")
    lines.append(f'orcaopta_device_info{{device="{device}"}} 1')

    gpu_all = snapshot.get("gpu", {}) or {}

    lines.append("# TYPE orcaopta_gpu_memory_total_bytes gauge")
    lines.append("# TYPE orcaopta_gpu_memory_allocated_bytes gauge")
    lines.append("# TYPE orcaopta_gpu_memory_reserved_bytes gauge")
    lines.append("# TYPE orcaopta_gpu_utilization_percent gauge")
    lines.append("# TYPE orcaopta_gpu_memory_utilization_percent gauge")
    lines.append("# TYPE orcaopta_gpu_temperature_celsius gauge")
    lines.append("# TYPE orcaopta_gpu_power_watts gauge")

    for idx, gpu in gpu_all.items():
        gpu_device = gpu.get("device", "cpu")
        gpu_name = gpu.get("gpu_name", "none")
        mem_total = gpu.get("memory_total", 0)
        mem_alloc = gpu.get("memory_allocated", 0)
        mem_res = gpu.get("memory_reserved", 0)
        util_gpu = gpu.get("util_gpu", 0)
        util_mem = gpu.get("util_mem", 0)
        temp = gpu.get("temperature", 0)
        power = gpu.get("power", 0)

        labels = f'device="{gpu_device}",gpu_name="{gpu_name}",gpu_index="{idx}"'

        lines.append(f"orcaopta_gpu_memory_total_bytes{{{labels}}} {mem_total}")
        lines.append(f"orcaopta_gpu_memory_allocated_bytes{{{labels}}} {mem_alloc}")
        lines.append(f"orcaopta_gpu_memory_reserved_bytes{{{labels}}} {mem_res}")
        lines.append(f"orcaopta_gpu_utilization_percent{{{labels}}} {util_gpu}")
        lines.append(f"orcaopta_gpu_memory_utilization_percent{{{labels}}} {util_mem}")
        lines.append(f"orcaopta_gpu_temperature_celsius{{{labels}}} {temp}")
        lines.append(f"orcaopta_gpu_power_watts{{{labels}}} {power}")

    ceph = snapshot.get("ceph", {}) or {}
    ceph_status = ceph.get("status", "unknown")
    lines.append("# TYPE orcaopta_ceph_status gauge")
    lines.append(f'orcaopta_ceph_status{{status="{ceph_status}"}} 1')

    k8s = snapshot.get("k8s", {}) or {}
    k8s_status = k8s.get("status", "unknown") if isinstance(k8s, dict) else "ok"
    lines.append("# TYPE orcaopta_k8s_status gauge")
    lines.append(f'orcaopta_k8s_status{{status="{k8s_status}"}} 1')

    ml = snapshot.get("ml") or {}
    autoscale_signal = ml.get("autoscale") or []
    lines.append("# TYPE orcaopta_ml_autoscale_signal gauge")
    for idx, v in enumerate(autoscale_signal):
        lines.append(f'orcaopta_ml_autoscale_signal{{index="{idx}"}} {v}')

    rl = snapshot.get("rl") or {}
    if isinstance(rl, dict):
        for key, value in rl.items():
            if isinstance(value, (int, float)):
                lines.append("# TYPE orcaopta_rl_metric gauge")
                lines.append(f'orcaopta_rl_metric{{name="{key}"}} {value}')

    return "\n".join(lines) + "\n"


# ============================================================
# ASYNC SUPERVISOR SERVICE
# ============================================================

class SupervisorService:
    def __init__(self, interval: int = 10):
        self.interval = interval
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self._latest_metrics: Dict[str, Any] = {}

    async def _loop(self):
        logger.info("Supervisor async loop started.")
        logger.info(f"Device: {DEVICE.upper()}")

        global _last_decision

        while self.running:
            try:
                metrics = collect_metrics_snapshot()
                self._latest_metrics = metrics

                logger.info(f"[Metrics] Snapshot: {metrics}")

                gpu_all = metrics.get("gpu", {}) or {}
                ml = metrics.get("ml") or {}

                decision = decide_autoscale_from_signals(
                    gpu_all=gpu_all,
                    ml=ml,
                    last_decision=_last_decision,
                )

                if decision:
                    apply_autoscale_decision(decision)

            except Exception as e:
                logger.error(f"Supervisor error: {e}")

            await asyncio.sleep(self.interval)

        logger.info("Supervisor async loop stopped.")

    def start(self):
        if self.running:
            logger.info("Supervisor already running.")
            return {"status": "already_running"}

        run_initial_autoscale()
        run_initial_jobs()

        self.running = True
        self.task = asyncio.create_task(self._loop())
        logger.info("Supervisor started.")
        return {"status": "supervisor_started"}

    def stop(self):
        if not self.running:
            return {"status": "not_running"}

        self.running = False
        logger.info("Supervisor stopping...")
        return {"status": "supervisor_stopped"}

    def get_health(self) -> Dict[str, Any]:
        return {
            "status": "running" if self.running else "stopped",
            "device": DEVICE,
            "ceph": ceph_health(),
            "k8s": k8s_health(),
            "gpu": gpu_status_multi(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        return self._latest_metrics or collect_metrics_snapshot()

    def get_metrics_prometheus(self) -> str:
        snapshot = self._latest_metrics or collect_metrics_snapshot()
        return metrics_to_prometheus(snapshot)


# ============================================================
# ENTRYPOINTS
# ============================================================

def start_supervisor(interval: int = 10) -> SupervisorService:
    global _supervisor_service
    if _supervisor_service is None:
        _supervisor_service = SupervisorService(interval=interval)
        _supervisor_service.start()
    return _supervisor_service


def get_supervisor() -> Optional[SupervisorService]:
    return _supervisor_service
