import joblib
from .config import *

def load_anomaly():
    return joblib.load(ANOMALY_MODEL)

def load_forecast():
    return joblib.load(FORECAST_MODEL)

def load_resource_opt():
    return joblib.load(RESOURCE_MODEL)

def load_autoscale():
    return joblib.load(AUTOSCALE_MODEL)
