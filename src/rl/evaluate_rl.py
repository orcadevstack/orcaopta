from src.rl.env_autoscale import AutoscaleEnv
from src.rl.agent_ppo import PPOAgent
import torch
import numpy as np

def evaluate(agent, episodes=50):
    env = AutoscaleEnv()
    returns = []

    for _ in range(episodes):
        state = env.reset()
        done = False
        ep_return = 0

        while not done:
            state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            logits = agent.policy(state_t)
            probs = torch.softmax(logits, dim=-1)
            action = torch.argmax(probs, dim=-1).item()

            next_state, reward, done, _ = env.step(action)
            ep_return += reward
            state = next_state

        returns.append(ep_return)

    print(f"Average return over {episodes} episodes: {np.mean(returns):.3f}")
    return returns

if __name__ == "__main__":
    # Load or reuse trained agent here
    pass
