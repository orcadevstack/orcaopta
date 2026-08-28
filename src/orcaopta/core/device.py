import torch
import logging
import platform

logger = logging.getLogger("orcaopta.device")

def gpu_available():
    try:
        return torch.cuda.is_available()
    except Exception as e:
        logger.warning(f"GPU check failed: {e}")
        return False

def get_device():
    if gpu_available():
        gpu_name = torch.cuda.get_device_name(0)
        capability = torch.cuda.get_device_capability(0)
        logger.info(f"GPU detected: {gpu_name} (Compute Capability {capability})")
        return "cuda"
    else:
        logger.warning("⚠ No GPU detected — falling back to CPU.")
        logger.info(f"CPU: {platform.processor()}")
        return "cpu"

device = get_device()
