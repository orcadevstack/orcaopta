import logging
import pandas as pd
from pathlib import Path
from flask import Flask, request, jsonify

from orcaopta.core.mode import detect_mode

from orcaopta.core.config import (
    load_config,
    get_database_config,
    get_cloud_storage_config,
    get_model_config,
    get_queue_config,
    get_ai_config,
    get_autoscaling_config,
)

from orcaopta.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
)

app = Flask(__name__)
logger = logging.getLogger("orcaopta-flask")

# Load YAML config once
config = load_config("orcaopta.yaml")



MODEL_CACHE = {
    "anomaly": None,
    "forecast": None,
    "resource_opt": None,
    "autoscale": None,
}

def load_models_once():
    logger.info("Loading ML models into Flask cache...")

    try:
        MODEL_CACHE["anomaly"] = model_utils.load_anomaly()
        MODEL_CACHE["forecast"] = model_utils.load_forecast()
        MODEL_CACHE["resource_opt"] = model_utils.load_resource_opt()
        MODEL_CACHE["autoscale"] = model_utils.load_autoscale()

        logger.info("Flask ML models loaded successfully.")

    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        raise

load_models_once()


def to_df(data):
    if not isinstance(data, dict):
        return None, "Payload must be a JSON object"

    if "records" not in data:
        return None, "Missing 'records' field"

    try:
        df = pd.DataFrame(data["records"])
        return df, None
    except Exception as e:
        return None, f"Invalid records format: {e}"


def error(message):
    logger.error(message)
    return jsonify({"error": message}), 400



@app.get("/system/config")
def system_config():
    cfg = load_config()
    return jsonify({
        "status": "ok",
        "config": cfg
    })


@app.get("/system/mode")
def system_mode():
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
    cloud_status = "enabled" if cloud_cfg.get("enabled", False) else "disabled"

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

    queue_cfg = get_queue_config()
    queue_backend = queue_cfg.get("backend", "local")


    autoscale_cfg = get_autoscaling_config()
    autoscale_enabled = autoscale_cfg.get("enabled", True)

    ai_cfg = get_ai_config()
    ai_provider = ai_cfg.get("llm", {}).get("provider")
    ai_model = ai_cfg.get("llm", {}).get("model")


    return jsonify({
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
    })



@app.post("/anomaly")
def anomaly():
    df, err = to_df(request.json)
    if err:
        return error(err)

    model = MODEL_CACHE["anomaly"]
    try:
        preds = anomaly_detection.predict_anomaly(model, df)
        return jsonify({"predictions": preds.tolist()})
    except Exception as e:
        return error(f"Anomaly detection failed: {e}")


@app.post("/forecast")
def forecast():
    df, err = to_df(request.json)
    if err:
        return error(err)

    model = MODEL_CACHE["forecast"]
    try:
        preds = forecasting.predict_future(model, df)
        return jsonify({"predictions": preds.tolist()})
    except Exception as e:
        return error(f"Forecasting failed: {e}")


@app.post("/resource-opt")
def resource_opt():
    df, err = to_df(request.json)
    if err:
        return error(err)

    model = MODEL_CACHE["resource_opt"]
    try:
        preds = resource_optimization.optimize_resources(model, df)
        return jsonify({"predictions": preds.tolist()})
    except Exception as e:
        return error(f"Resource optimization failed: {e}")


@app.post("/autoscale")
def autoscale():
    df, err = to_df(request.json)
    if err:
        return error(err)

    model = MODEL_CACHE["autoscale"]
    try:
        preds = autoscaling.autoscale_decision(model, df)
        return jsonify({"decisions": preds.tolist()})
    except Exception as e:
        return error(f"Autoscale decision failed: {e}")


@app.post("/spark/run")
async def spark_run(job: str):
    return mcp.handle(MCPRequest(tool="spark_run_job", arguments={"job_name": job}))

