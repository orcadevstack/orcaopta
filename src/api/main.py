import logging
import subprocess
import pandas as pd
import mlflow

from fastapi import FastAPI, Request
from pydantic import BaseModel

from src.orcaopta.core.mode import detect_mode
from src.orcaopta.core.config import load_config
from src.orcaopta.core.events import get_events

from src.orcaopta.cloud.graph import build_cloud_graph

from src.utils.tracing import setup_tracing
from src.core.security.encryption import encrypt, decrypt

from src.orcaopta.ai.agent import (
    ai_self_heal_plan,
    ai_explain_anomaly,
    ai_explain_forecast,
    ai_explain_autoscale,
)

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
)

logger = logging.getLogger("orcaopta")

MODEL_NAME = "orcaopta-ml"
MODEL_STAGE = "Production"

config = None
model = None
tracer = None

app = FastAPI(title="Orcaopta ML API")



def configure_mlflow_auto():
    mode = detect_mode()

    if mode == "standalone":
        uri = "sqlite:///mlflow.db"
        logger.info("MLflow running in STANDALONE mode (SQLite + local filesystem).")
    else:
        uri = "http://mlflow:5000"
        logger.info("MLflow running in CLUSTER mode (Postgres + MinIO).")

    mlflow.set_tracking_uri(uri)
    return uri



@app.get("/dashboard/heal-mode")
def get_heal_mode():
    return {"mode": detect_mode()}


@app.get("/dashboard/heal-status")
def get_heal_status():
    from src.orcaopta.controller.self_heal import (
        is_openstack_available,
        is_kubernetes_available,
        is_terraform_available,
        is_ceph_available,
        is_cloud_graph_available,
    )

    return {
        "mode": detect_mode(),
        "cloud_graph": is_cloud_graph_available(),
        "openstack": is_openstack_available(),
        "kubernetes": is_kubernetes_available(),
        "terraform": is_terraform_available(),
        "ceph": is_ceph_available(),
    }



class Payload(BaseModel):
    records: list[dict]


def load_model():
    global model
    logger.info("Loading MLflow model...")
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
    logger.info("Model loaded successfully")


@app.on_event("startup")
def startup_event():
    global config, tracer

    logger.info("Starting ORCAOPTA API...")

    # Load config
    config = load_config()

    # Tracing
    tracer = setup_tracing()
    logger.info("Tracing initialized")

    # MLflow auto-switch
    uri = configure_mlflow_auto()
    logger.info(f"MLflow tracking URI set to: {uri}")

    # Load model
    try:
        load_model()
    except Exception as e:
        logger.error(f"Model load failed: {e}")

    # Optional: security audit
    try:
        audit_results = subprocess.check_output(["ossaudit", "scan", "."]).decode()
        plan = ai_self_heal_plan([{"audit": audit_results}])
        logger.info("Startup security self-heal plan generated.")
    except Exception as e:
        logger.warning(f"Security audit failed at startup: {e}")



@app.post("/store-secret")
def store_secret(payload: dict):
    encrypted = encrypt(payload["value"].encode())
    return {"token": encrypted.decode()}


@app.post("/read-secret")
def read_secret(payload: dict):
    decrypted = decrypt(payload["token"].encode())
    return {"value": decrypted.decode()}



@app.get("/predict")
def predict(x: float):
    y = model.predict([[x]])[0]
    return {"input": x, "output": float(y)}


def to_df(payload: Payload):
    return pd.DataFrame(payload.records)


@app.post("/anomaly")
def anomaly(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_anomaly()
    preds = anomaly_detection.predict_anomaly(m, df)
    return {"predictions": preds.tolist()}


@app.post("/forecast")
def forecast(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_forecast()
    preds = forecasting.predict_future(m, df)
    return {"predictions": preds.tolist()}


@app.post("/resource-opt")
def resource_opt(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_resource_opt()
    preds = resource_optimization.optimize_resources(m, df)
    return {"predictions": preds.tolist()}


@app.post("/autoscale")
def autoscale(payload: Payload):
    df = to_df(payload)
    m = model_utils.load_autoscale()
    preds = autoscaling.autoscale_decision(m, df)
    return {"decisions": preds.tolist()}


@app.middleware("http")
async def trace_requests(request: Request, call_next):
    with tracer.start_as_current_span(f"HTTP {request.method} {request.url.path}") as span:
        span.set_attribute("method", request.method)
        span.set_attribute("path", request.url.path)
        span.set_attribute("client", request.client.host)

        response = await call_next(request)
        span.set_attribute("status_code", response.status_code)

        return response



@app.post("/ai/anomaly-explain")
def ai_anomaly_explain(payload: Payload):
    return {"explanation": ai_explain_anomaly(payload.records)}


@app.post("/ai/forecast-explain")
def ai_forecast_explain(payload: Payload):
    return {"explanation": ai_explain_forecast(payload.records)}


@app.post("/ai/autoscale-explain")
def ai_autoscale_explain(payload: Payload):
    return {"explanation": ai_explain_autoscale(payload.records)}


@app.post("/ai/self-heal-plan")
def ai_self_heal(payload: Payload):
    plan = ai_self_heal_plan(payload.records)
    return {"self_heal_plan": plan}


@app.get("/ai/global-self-heal")
def ai_global_self_heal():
    graph = build_cloud_graph()
    plan = ai_self_heal_plan([{"cloud_graph": graph}])
    return {"global_self_heal_plan": plan}



@app.get("/dashboard/cloud-graph")
def dashboard_cloud_graph():
    return {"graph": build_cloud_graph()}


@app.get("/dashboard/healing-events")
def dashboard_healing_events():
    return {"events": get_events()}


@app.get("/system/mode")
def system_mode():
    """
    Returns full system runtime mode:
    - MLflow backend
    - Database backend
    - Queue backend
    - Storage backend
    - Overall mode (standalone vs cluster)
    """
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

    return {
        "mode": mode,
        "mlflow_backend": mlflow_backend,
        "database_backend": db_backend,
        "queue_backend": queue_backend,
        "storage_backend": storage_backend,
    }

def start():
    subprocess.run(["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        start()