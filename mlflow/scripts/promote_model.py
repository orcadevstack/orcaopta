import mlflow

client = mlflow.MlflowClient()

MODEL_NAME = "orcaopta-ml"

latest_staging = client.get_latest_versions(MODEL_NAME, stages=["Staging"])[0]

client.transition_model_version_stage(
    name=MODEL_NAME,
    version=latest_staging.version,
    stage="Production"
)

print(f"Promoted {MODEL_NAME} v{latest_staging.version} → Production")

