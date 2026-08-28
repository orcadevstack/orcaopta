import sys
import json
import pandas as pd

from src.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
)


VALID_MODULES = {
    "anomaly_detection",
    "forecasting",
    "resource_optimization",
    "autoscaling",
}

def error(message):
    print(json.dumps({"error": message}))
    sys.exit(1)




if len(sys.argv) < 4:
    error("Usage: python python_bridge.py <module> <func> <records_json>")

module = sys.argv[1]
func = sys.argv[2]
records_json = sys.argv[3]

if module not in VALID_MODULES:
    error(f"Invalid module '{module}'. Valid modules: {list(VALID_MODULES)}")

try:
    records = json.loads(records_json)
except Exception as e:
    error(f"Invalid JSON payload: {e}")

if not isinstance(records, list):
    error("Records must be a list of objects")

if len(records) == 0:
    error("Records list is empty")

df = pd.DataFrame(records)




try:
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

    else:
        error(f"Unknown module '{module}'")

    print(json.dumps({"result": preds.tolist()}))

except Exception as e:
    error(f"Execution failed: {e}")
