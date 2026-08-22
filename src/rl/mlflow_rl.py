import mlflow
import mlflow.pytorch
from src.rl.train_rl import train_rl

def train_with_mlflow():
    mlflow.set_experiment("orcaopta-rl-autoscale")

    with mlflow.start_run():
        agent = train_rl(num_episodes=200)

        # Example: log model
        mlflow.pytorch.log_model(agent.policy, "policy_net")
        mlflow.pytorch.log_model(agent.value, "value_net")

        mlflow.log_param("episodes", 200)
        print("RL training logged to MLflow.")

if __name__ == "__main__":
    train_with_mlflow()
