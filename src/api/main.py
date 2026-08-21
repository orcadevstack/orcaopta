from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling
)

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
