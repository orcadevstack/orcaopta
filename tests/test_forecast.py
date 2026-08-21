from src.ml import forecasting, model_utils
import pandas as pd

def test_forecast_predict():
    model = model_utils.load_forecast()
    df = pd.DataFrame({"cpu_usage": [0.5]})
    preds = forecasting.predict_future(model, df)
    assert len(preds) == 1
