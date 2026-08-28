from flask import Flask, request, jsonify
import pandas as pd
import logging

from src.orcaopta.core.mode import detect_mode
from src.orcaopta.core.config import load_config

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
)

app = Flask(__name__)
logger = logging.getLogger("orcaopta-flask")

config = load_config()



MODEL_CACHE = {
    "anomaly": None,
    "forecast": None,
    "resource_opt": None,
    "autoscale": None,
}

def load_models_once():
    logger.info("Loading ML models into Flask cache...")

    MODEL_CACHE["anomaly"] = model_utils.load_anomaly()
    MODEL_CACHE["forecast"] = model_utils.load_forecast()
    MODEL_CACHE["resource_opt"] = model_utils.load_resource_opt()
    MODEL_CACHE["autoscale"] = model_utils.load_autoscale()

    logger.info("Flask ML models loaded successfully.")


load_models_once()



def to_df(data):
    if "records" not in data:
        return None, "Missing 'records' field"

    try:
        df = pd.DataFrame(data["records"])
        return df, None
    except Exception as e:
        return None, f"Invalid records format: {e}"


def error(message):
    return jsonify({"error": message}), 400




@app.get("/system/mode")
def system_mode():
    mode = detect_mode()

    if mode == "standalone":
        mlflow_backend = "sqlite:///mlflow.db"
        storage_backend = "local filesystem (./mlruns)"
        db_backend = "sqlite:///orcaopta.db"
        queue_backend = "in-memory queue"
    else:
        mlflow_backend = "http://mlflow:5000"
        storage_backend = "MinIO (s3://orcaopta-artifacts)"
        db_backend = "Postgres"
        queue_backend = "Redis"

    return jsonify({
        "mode": mode,
        "mlflow_backend": mlflow_backend,
        "database_backend": db_backend,
        "queue_backend": queue_backend,
        "storage_backend": storage_backend,
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
