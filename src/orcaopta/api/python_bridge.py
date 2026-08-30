import sys
import json
import pandas as pd
import traceback

from orcaopta.ml import (
    model_utils,
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
)

VALID_MODULES = {
    "anomaly_detection": anomaly_detection.predict_anomaly,
    "forecasting": forecasting.predict_future,
    "resource_optimization": resource_optimization.optimize_resources,
    "autoscaling": autoscaling.autoscale_decision,
}

def error(message, details=None):
    payload = {"error": message}
    if details:
        payload["details"] = details
    print(json.dumps(payload))
    sys.exit(1)


if len(sys.argv) < 4:
    error("Usage: python python_bridge.py <module> <func> <records_json>")

module = sys.argv[1]
func = sys.argv[2]  # currently unused but kept for future extension
records_json = sys.argv[3]

if module not in VALID_MODULES:
    error(
        f"Invalid module '{module}'.",
        f"Valid modules: {list(VALID_MODULES.keys())}"
    )


try:
    records = json.loads(records_json)
except Exception as e:
    error("Invalid JSON payload", str(e))

if not isinstance(records, list):
    error("Records must be a list of objects")

if len(records) == 0:
    error("Records list is empty")

df = pd.DataFrame(records)


try:
   
    if module == "anomaly_detection":
        model = model_utils.load_anomaly()

    elif module == "forecasting":
        model = model_utils.load_forecast()

    elif module == "resource_optimization":
        model = model_utils.load_resource_opt()

    elif module == "autoscaling":
        model = model_utils.load_autoscale()

    else:
        error(f"Unknown module '{module}'")

    # Execute prediction function
    predict_fn = VALID_MODULES[module]
    preds = predict_fn(model, df)

    # Output result
    print(json.dumps({"result": preds.tolist()}))

except Exception as e:
    tb = traceback.format_exc()
    error("Execution failed", tb)
