from src.ml import anomaly_detection, model_utils
import pandas as pd

def test_anomaly_model_loads():
    model = model_utils.load_anomaly()
    assert model is not None
