from src.rl.env_autoscale import AutoscaleEnv
from src.rl.agent_ppo import PPOAgent
import numpy as np

def train_rl(num_episodes=500):
    env = AutoscaleEnv()
    state_dim = env._get_state().shape[0]
    action_dim = 3  # scale_down, hold, scale_up

    agent = PPOAgent(state_dim, action_dim)

    for episode in range(num_episodes):
        state = env.reset()
        done = False

        states = []
        actions = []
        rewards = []
        log_probs = []

        while not done:
            action, log_prob = agent.act(state)
            next_state, reward, done, _ = env.step(action)

            states.append(state)
            actions.append(action)
            rewards.append(reward)
            log_probs.append(log_prob.detach())

            state = next_state

        policy_loss, value_loss = agent.update(
            states,
            actions,
            torch.stack(log_probs),
            rewards
        )

        ep_return = sum(rewards)
        print(f"Episode {episode} | Return: {ep_return:.3f} | Policy loss: {policy_loss:.3f} | Value loss: {value_loss:.3f}")

    return agent

if __name__ == "__main__":
    agent = train_rl()
