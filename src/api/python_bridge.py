import sys, json, pandas as pd
from src.ml import model_utils, anomaly_detection, forecasting, resource_optimization, autoscaling

module = sys.argv[1]
func = sys.argv[2]
records = json.loads(sys.argv[3])

df = pd.DataFrame(records)

if module == "anomaly_detection":
    model = model_utils.load_anomaly()
    preds = anomaly_detection.predict_anomaly(model, df)

elif module == "forecasting":
    model = model_utils.load_forecast()
    preds = forecasting.predict_future(model, df)

elif module == "resource_optimization":
    model = model_utils.load_resource_opt()
    preds = resource_optimization.optimize_resources(model, df)

elif module == "autoscaling":
    model = model_utils.load_autoscale()
    preds = autoscaling.autoscale_decision(model, df)

print(json.dumps({"result": preds.tolist()}))
