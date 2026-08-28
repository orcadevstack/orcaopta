import time
import logging
import shutil
import subprocess
import json

from orcaopta.utils.device import device

# ML/RL optional imports
try:
    from src.ml import anomaly_detection, forecasting, resource_optimization, autoscaling, model_utils
except ImportError:
    anomaly_detection = forecasting = resource_optimization = autoscaling = model_utils = None

try:
    from src.rl import evaluate_rl, agent_ppo
except ImportError:
    evaluate_rl = agent_ppo = None

logger = logging.getLogger("orcaopta.supervisor")



def ceph_health():
    if not shutil.which("ceph"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["ceph", "health", "-f", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def k8s_health():
    if not shutil.which("kubectl"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def gpu_status():
    if device == "cuda":
        import torch
        props = torch.cuda.get_device_properties(0)
        return {
            "device": "cuda",
            "gpu_name": torch.cuda.get_device_name(0),
            "memory_total": props.total_memory,
            "memory_allocated": torch.cuda.memory_allocated(),
            "memory_reserved": torch.cuda.memory_reserved(),
        }
    return {"device": "cpu"}



def ml_signals():
    if not model_utils:
        return None

    df = model_utils.sample_cluster_metrics()

    return {
        "anomaly": anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df).tolist(),
        "forecast": forecasting.predict_future(model_utils.load_forecast(), df).tolist(),
        "resource_opt": resource_optimization.optimize_resources(
            model_utils.load_resource_opt(), df
        ).tolist(),
        "autoscale": autoscaling.autoscale_decision(
            model_utils.load_autoscale(), df
        ).tolist(),
    }


def rl_signals():
    if not agent_ppo:
        return None

    agent = agent_ppo.load_agent()
    return evaluate_rl.evaluate_agent(agent)



def start_supervisor(interval: int = 10):
    """
    Main supervisor loop:
    - monitors GPU/CPU load
    - monitors Ceph/K8s health
    - monitors ML/RL signals
    - triggers autoscaling or healing
    """

    logger.info("🚀 Orcaopta Supervisor started")
    logger.info(f"Device: {device.upper()}")

    while True:
        try:
            # GPU
            gpu = gpu_status()
            logger.info(f"[GPU] {gpu}")

            # Ceph
            ceph = ceph_health()
            logger.info(f"[Ceph] {ceph}")

            # Kubernetes
            k8s = k8s_health()
            logger.info(f"[K8s] {k8s}")

            # ML signals
            ml = ml_signals()
            if ml:
                logger.info(f"[ML] {ml}")

            # RL signals
            rl = rl_signals()
            if rl:
                logger.info(f"[RL] {rl}")

            if ml and ml.get("autoscale") == "scale_up":
                logger.warning("⚠ Autoscale signal detected: SCALE UP")
                # TODO: integrate with K8s or OpenStack scaling

            if ml and ml.get("autoscale") == "scale_down":
                logger.warning("⚠ Autoscale signal detected: SCALE DOWN")
                # TODO: integrate with K8s or OpenStack scaling

        except Exception as e:
            logger.error(f"Supervisor error: {e}")

        time.sleep(interval)
