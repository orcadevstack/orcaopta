import mlflow
import os

def configure_mlflow_standalone(cfg):
    backend = cfg["standalone"]["mlflow_backend"]
    artifacts = cfg["standalone"]["mlflow_artifacts"]

    os.makedirs(artifacts, exist_ok=True)

    mlflow.set_tracking_uri(backend)
    mlflow.set_experiment("orcaopta-local")

    print(f"MLflow standalone mode: backend={backend}, artifacts={artifacts}")
