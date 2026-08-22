from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, Request
from src.utils.tracing import setup_tracing
import pandas as pd

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling
)


tracer = setup_tracing()
app = FastAPI()

app = FastAPI(title="orcaopta ML API")

class Payload(BaseModel):
    records: list[dict]

def to_df(payload: Payload):
    return pd.DataFrame(payload.records)

@app.post("/anomaly")
def anomaly(payload: Payload):
    df = to_df(payload)
    model = model_utils.load_anomaly()
    preds = anomaly_detection.predict_anomaly(model, df)
    return {"predictions": preds.tolist()}

@app.post("/forecast")
def forecast(payload: Payload):
    df = to_df(payload)
    model = model_utils.load_forecast()
    preds = forecasting.predict_future(model, df)
    return {"predictions": preds.tolist()}

@app.post("/resource-opt")
def resource_opt(payload: Payload):
    df = to_df(payload)
    model = model_utils.load_resource_opt()
    preds = resource_optimization.optimize_resources(model, df)
    return {"predictions": preds.tolist()}

@app.post("/autoscale")
def autoscale(payload: Payload):
    df = to_df(payload)
    model = model_utils.load_autoscale()
    preds = autoscaling.autoscale_decision(model, df)
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
