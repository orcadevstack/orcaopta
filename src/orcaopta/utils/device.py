import logging
import platform

logger = logging.getLogger("orcaopta.device")

# ============================================================
# GPU CHECK (SAFE)
# ============================================================

def gpu_available():
    """
    Safely check if CUDA GPU is available.
    Returns True/False.
    """
    try:
        import torch
        return torch.cuda.is_available()
    except Exception as e:
        logger.warning(f"[Device] GPU check failed: {e}")
        return False


# ============================================================
# GPU INFO (SAFE)
# ============================================================

def get_gpu_info():
    """
    Returns detailed GPU info if available.
    Otherwise returns None.
    """
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


# ============================================================
# DEVICE DETECTION (ENTERPRISE-GRADE)
# ============================================================

def detect_device():
    """
    Enterprise-grade device selector.
    Returns 'cuda' or 'cpu'.
    Logs full hardware details.
    """
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

    # CPU fallback
    cpu_name = platform.processor() or "Unknown CPU"
    logger.warning("[Device] ⚠ No GPU detected — falling back to CPU.")
    logger.info(f"[Device] CPU detected: {cpu_name}")

    return "cpu"


# ============================================================
# PUBLIC CONSTANT (THIS IS WHAT SUPERVISOR IMPORTS)
# ============================================================

DEVICE = detect_device()

logger.info(f"[Device] Active device: {DEVICE.upper()}")
