from src.ml import resource_optimization, model_utils
import pandas as pd

def test_resource_opt():
    model = model_utils.load_resource_opt()
    df = pd.DataFrame({"cpu": [0.5], "ram": [0.7]})
    preds = resource_optimization.optimize_resources(model, df)
    assert len(preds) == 1
