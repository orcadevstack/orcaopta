from src.ml import autoscaling, model_utils
import pandas as pd

def test_autoscale():
    model = model_utils.load_autoscale()
    df = pd.DataFrame({"cpu": [0.9], "requests": [200]})
    preds = autoscaling.autoscale_decision(model, df)
    assert len(preds) == 1
