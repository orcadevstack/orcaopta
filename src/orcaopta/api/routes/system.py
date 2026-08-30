from fastapi import APIRouter
from pathlib import Path

from src.orcaopta.core.config import (
    load_config,
    get_database_config,
    get_cloud_storage_config,
    get_model_config,
    get_queue_config,
    get_ai_config,
    get_autoscaling_config,
)

router = APIRouter()


# ============================================================
# /system/config
# ============================================================

@router.get("/system/config")
def system_config():
    """
    Return the full Orcaopta configuration loaded from orcaopta.yaml.
    """
    cfg = load_config()
    return {
        "status": "ok",
        "config": cfg
    }


# ============================================================
# /system/mode
# ============================================================

@router.get("/system/mode")
def system_mode():
    """
    Return the full Orcaopta runtime mode:
    - database backend
    - cloud storage status
    - model registry status
    - queue backend
    - autoscaling engine
    - AI engine
    """

    # -------------------------
    # Database
    # -------------------------
    db_cfg = get_database_config()
    db_url = db_cfg.get("url", "sqlite:///orcaopta.db")

    if db_url.startswith("sqlite"):
        db_backend = "SQLite"
    elif db_url.startswith("postgres"):
        db_backend = "PostgreSQL"
    elif db_url.startswith("mysql"):
        db_backend = "MySQL"
    else:
        db_backend = "Unknown"

    # -------------------------
    # Cloud Storage
    # -------------------------
    cloud_cfg = get_cloud_storage_config()
    cloud_enabled = cloud_cfg.get("enabled", False)
    cloud_status = "enabled" if cloud_enabled else "disabled"

    # -------------------------
    # Model Registry
    # -------------------------
    model_cfg = get_model_config()
    model_dir = Path(model_cfg.get("directory", "/app/models"))

    registry_status = {
        "exists": model_dir.exists(),
        "path": str(model_dir),
        "models": {
            "anomaly": model_cfg.get("anomaly", {}),
            "forecast": model_cfg.get("forecast", {}),
            "resource_opt": model_cfg.get("resource_opt", {}),
            "autoscale": model_cfg.get("autoscale", {}),
        }
    }

    # -------------------------
    # Queue Backend
    # -------------------------
    queue_cfg = get_queue_config()
    queue_backend = queue_cfg.get("backend", "local")

    # -------------------------
    # Autoscaling Engine
    # -------------------------
    autoscale_cfg = get_autoscaling_config()
    autoscale_enabled = autoscale_cfg.get("enabled", True)

    # -------------------------
    # AI Engine
    # -------------------------
    ai_cfg = get_ai_config()
    ai_provider = ai_cfg.get("llm", {}).get("provider", "unknown")
    ai_model = ai_cfg.get("llm", {}).get("model", "unknown")

    # -------------------------
    # Final Response
    # -------------------------
    return {
        "status": "ok",
        "database": {
            "backend": db_backend,
            "url": db_url,
        },
        "cloud_storage": {
            "status": cloud_status,
            "endpoint": cloud_cfg.get("endpoint"),
            "bucket": cloud_cfg.get("bucket"),
        },
        "model_registry": registry_status,
        "queue": {
            "backend": queue_backend,
            "redis_url": queue_cfg.get("redis_url"),
        },
        "autoscaling": {
            "enabled": autoscale_enabled,
            "min_replicas": autoscale_cfg.get("min_replicas"),
            "max_replicas": autoscale_cfg.get("max_replicas"),
        },
        "ai_engine": {
            "provider": ai_provider,
            "model": ai_model,
        }
    }
