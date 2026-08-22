import mlflow

client = mlflow.MlflowClient()

MODEL_NAME = "orcaopta-ml"

versions = client.search_model_versions(f"name='{MODEL_NAME}'")

for v in versions:
    print(f"Version {v.version} | Stage: {v.current_stage} | Run ID: {v.run_id}")
