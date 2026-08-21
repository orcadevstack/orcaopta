from flask import Flask, request, jsonify
import pandas as pd

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling
)

app = Flask(__name__)

def to_df(data):
    return pd.DataFrame(data["records"])

@app.post("/anomaly")
def anomaly():
    df = to_df(request.json)
    model = model_utils.load_anomaly()
    preds = anomaly_detection.predict_anomaly(model, df)
    return jsonify({"predictions": preds.tolist()})

@app.post("/forecast")
def forecast():
    df = to_df(request.json)
    model = model_utils.load_forecast()
    preds = forecasting.predict_future(model, df)
    return jsonify({"predictions": preds.tolist()})

@app.post("/resource-opt")
def resource_opt():
    df = to_df(request.json)
    model = model_utils.load_resource_opt()
    preds = resource_optimization.optimize_resources(model, df)
    return jsonify({"predictions": preds.tolist()})

@app.post("/autoscale")
def autoscale():
    df = to_df(request.json)
    model = model_utils.load_autoscale()
    preds = autoscaling.autoscale_decision(model, df)
    return jsonify({"decisions": preds.tolist()})
