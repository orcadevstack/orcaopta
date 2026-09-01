"""
Training loop for autoscale RL environment + agent.
"""

from typing import List, Dict
from orcaopta.ml.rl.envs.autoscale_env import AutoscaleEnv
from orcaopta.ml.rl.agents.ppo_agent import PPOAgent


def train_autoscale(env: AutoscaleEnv, agent: PPOAgent, episodes: int = 10) -> None:
    """
    Minimal training loop skeleton.
    """
    for _ in range(episodes):
        state = env.reset(initial_state={})
        done = False
        trajectory: List[Dict] = []

        while not done:
            action = agent.act(state)
            next_state, reward, done, info = env.step(action, next_state=state)
            trajectory.append({"state": state, "action": action, "reward": reward})
            state = next_state

        agent.update(trajectory)
