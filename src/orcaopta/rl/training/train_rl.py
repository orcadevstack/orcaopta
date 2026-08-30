import torch
import numpy as np

from orcaopta.tracking.client import OrcaoptaTracker
from src.orcaopta.rl.envs.autoscale_env import AutoscaleEnv
from src.orcaopta.rl.agents.ppo_agent import PPOAgent
from orcaopta.utils.tracing import setup_tracing

tracker = OrcaoptaTracker()
tracer = setup_tracing()


def train_autoscale_rl(num_episodes=500):
    env = AutoscaleEnv()
    state_dim = len(env.reset())
    action_dim = 3  # scale_down, hold, scale_up

    agent = PPOAgent(state_dim, action_dim)

    with tracer.start_as_current_span("rl-training") as span:
        span.set_attribute("agent", "PPO")
        span.set_attribute("environment", "orcaopta-autoscale")

        for episode in range(num_episodes):

            with tracer.start_as_current_span(f"episode-{episode}") as ep_span:
                ep_span.set_attribute("episode", episode)

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

                # PPO update
                policy_loss, value_loss = agent.update(
                    states,
                    actions,
                    torch.stack(log_probs),
                    rewards
                )

                ep_return = float(sum(rewards))

                # Logging
                tracker.log_metric("rl_autoscale_reward", ep_return, {"episode": episode})
                tracker.log_event("rl_autoscale_episode", "rl", {
                    "episode": episode,
                    "reward": ep_return,
                    "policy_loss": policy_loss,
                    "value_loss": value_loss
                })

                print(
                    f"Episode {episode} | "
                    f"Return: {ep_return:.3f} | "
                    f"Policy loss: {policy_loss:.3f} | "
                    f"Value loss: {value_loss:.3f}"
                )

    # Save trained agent
    agent.save("/app/models/rl/autoscale_ppo.pkl")
    tracker.log_event("rl_model_saved", "rl", {"path": "/app/models/rl/autoscale_ppo.pkl"})

    return agent


if __name__ == "__main__":
    train_autoscale_rl()
