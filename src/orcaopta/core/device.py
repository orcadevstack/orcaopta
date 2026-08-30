import logging
import platform

logger = logging.getLogger("orcaopta.device")

def gpu_available():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception as e:
        logger.warning(f"[Device] GPU check failed: {e}")
        return False

def get_gpu_info():
    try:
        import torch
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            return {
                "name": torch.cuda.get_device_name(0),
                "capability": torch.cuda.get_device_capability(0),
                "memory_total": props.total_memory,
            }
    except Exception as e:
        logger.warning(f"[Device] Failed to read GPU info: {e}")
    return None

def detect_device():
    gpu_info = get_gpu_info()
    if gpu_info:
        logger.info(
            f"[Device] GPU detected: {gpu_info['name']} "
            f"(Compute Capability {gpu_info['capability']})"
        )
        logger.info(
            f"[Device] GPU Memory: {gpu_info['memory_total'] / (1024**3):.2f} GB"
        )
        return "cuda"

    cpu_name = platform.processor() or "Unknown CPU"
    logger.warning("[Device] ⚠ No GPU detected — falling back to CPU.")
    logger.info(f"[Device] CPU detected: {cpu_name}")
    return "cpu"

# THIS MUST EXIST — THIS IS WHAT SUPERVISOR IMPORTS
DEVICE = detect_device()

logger.info(f"[Device] Active device: {DEVICE.upper()}")
