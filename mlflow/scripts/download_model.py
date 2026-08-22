import mlflow

MODEL_NAME = "orcaopta-ml"
STAGE = "Production"

model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{STAGE}")

print("Model downloaded successfully.")
