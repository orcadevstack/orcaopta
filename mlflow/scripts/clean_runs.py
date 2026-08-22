import mlflow

client = mlflow.MlflowClient()

experiment_id = "0"

runs = client.list_run_infos(experiment_id)

for run in runs:
    client.delete_run(run.run_id)
    print(f"Deleted run: {run.run_id}")
