from fastapi import FastAPI, Request
from src.orcaopta.ai.agent import ai_self_heal_plan
from src.utils.tracing import setup_tracing
from src.core.security.encryption import encrypt, decrypt
from src.orcaopta.core.events import get_events
from src.orcaopta.cloud.graph import build_cloud_graph


from pydantic import BaseModel
import pandas as pd
import mlflow
import logging

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling
)


logger = logging.getLogger("orcaopta")
MODEL_NAME = "orcaopta-ml"
MODEL_STAGE = "Production"
model = None
tracer = None

audit_results = subprocess.check_output(["ossaudit", "scan", "."]).decode()
plan = ai_self_heal_plan([{"audit": audit_results}])
print(plan)

from src.orcaopta.ai.agent import (
    ai_explain_anomaly,
    ai_explain_forecast,
    ai_explain_autoscale,
)


app = FastAPI(title="orcaopta ML API")


class Payload(BaseModel):
    records: list[dict]


def load_model():
    global model
    logger.info("Loading MLflow model...")
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
    logger.info("Model loaded successfully")


@app.on_event("startup")
def startup_event():
    global tracer

    logger.info("Starting ORCAOPTA API...")

    # Initialize tracing
    tracer = setup_tracing()
    logger.info("Tracing initialized")

    # Configure MLflow
    mlflow.set_tracking_uri("http://mlflow:5000")
    logger.info("MLflow tracking URI set")

    # Load model
    load_model()


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
    explanation = ai_explain_anomaly(payload.records)
    return {"explanation": explanation}


@app.post("/ai/forecast-explain")
def ai_forecast_explain(payload: Payload):
    explanation = ai_explain_forecast(payload.records)
    return {"explanation": explanation}


@app.post("/ai/autoscale-explain")
def ai_autoscale_explain(payload: Payload):
    explanation = ai_explain_autoscale(payload.records)
    return {"explanation": explanation}

@app.post("/ai/self-heal-plan")
def ai_self_heal(payload: Payload):
    """
    Generate a full AI-driven self-healing plan for the Orcaopta cluster.
    """
    plan = ai_self_heal_plan(payload.records)
    return {"self_heal_plan": plan}

@app.get("/ai/global-self-heal")
def ai_global_self_heal():
    graph = build_cloud_graph()
    plan = ai_self_heal_plan([{"cloud_graph": graph}])
    return {"global_self_heal_plan": plan}

@app.get("/dashboard/cloud-graph")
def dashboard_cloud_graph():
    graph = build_cloud_graph()
    return {"graph": graph}


@app.get("/dashboard/healing-events")
def dashboard_healing_events():
    events = get_events()
    return {"events": events}
