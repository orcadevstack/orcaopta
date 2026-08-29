import json
import os

from src.spark.pipelines.pipeline_main import run_pipeline

def load_config(path: str = "spark_config.json") -> dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def main():
    config = load_config()
    result = run_pipeline(config)
    print("=== SLO ===")
    print(result["slo"])
    print("=== Anomalies (sample) ===")
    result["anomalies_df"].show(20, truncate=False)

if __name__ == "__main__":
    main()
