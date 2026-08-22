import mlflow

from src.rl.env import make_env
from src.rl.agent import Agent

minio_key = decrypt(os.getenv("MINIO_KEY_ENC").encode()).decode()


def main():
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("orcaopta-rl")

    env = make_env()
    agent = Agent(env.observation_space, env.action_space)

    with mlflow.start_run():
        for episode in range(100):
            obs = env.reset()
            done = False
            total_reward = 0.0

            while not done:
                action = agent.act(obs)
                next_obs, reward, done, info = env.step(action)
                agent.learn(obs, action, reward, next_obs, done)
                obs = next_obs
                total_reward += reward

            mlflow.log_metric("episode_reward", total_reward, step=episode)

        mlflow.log_artifact("models/rl_agent.pt")

if __name__ == "__main__":
    main()
