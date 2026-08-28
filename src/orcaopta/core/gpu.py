from fastapi import APIRouter
import torch
from orcaopta.utils.device import device

router = APIRouter()

@router.get("/gpu")
def gpu_status():
    if device == "cuda":
        return {
            "device": "cuda",
            "gpu_name": torch.cuda.get_device_name(0),
            "capability": torch.cuda.get_device_capability(0),
            "memory_total": torch.cuda.get_device_properties(0).total_memory,
            "memory_allocated": torch.cuda.memory_allocated(),
            "memory_reserved": torch.cuda.memory_reserved(),
        }
    else:
        return {
            "device": "cpu",
            "warning": "No GPU detected — running on CPU."
        }
