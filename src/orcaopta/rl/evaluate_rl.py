import numpy as np
import torch

from src.orcaopta.rl.envs.autoscale_env import AutoscaleEnv
from src.orcaopta.rl.agents.ppo_agent import PPOAgent


def evaluate(agent: PPOAgent, episodes: int = 50):
    """
    Evaluate a trained PPO autoscale agent on the AutoscaleEnv.
    Uses greedy (argmax) policy instead of sampling.
    """
    env = AutoscaleEnv()
    returns = []

    for _ in range(episodes):
        state = env.reset()
        done = False
        ep_return = 0

        while not done:
            # Convert state → tensor
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)

            # Forward pass through policy network
            logits = agent.policy(state_t)
            probs = torch.softmax(logits, dim=-1)

            # Greedy action (best action)
            action = torch.argmax(probs, dim=-1).item()

            # Step environment
            next_state, reward, done, _ = env.step(action)
            ep_return += reward
            state = next_state

        returns.append(ep_return)

    avg_return = np.mean(returns)
    print(f"Average return over {episodes} episodes: {avg_return:.3f}")
    return returns


if __name__ == "__main__":
    # Example: load trained agent
    agent = PPOAgent(state_dim=6, action_dim=3)
    agent.load("/app/models/rl/autoscale_ppo.pkl")

    evaluate(agent, episodes=50)
