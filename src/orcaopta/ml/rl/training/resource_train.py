"""
Training loop for resource RL environment + agent.
"""

from typing import List, Dict
from orcaopta.ml.rl.envs.resource_env import ResourceEnv
from orcaopta.ml.rl.agents.ppo_agent import PPOAgent


def train_resource(env: ResourceEnv, agent: PPOAgent, episodes: int = 10) -> None:
    trajectory: List[Dict] = []

    for _ in range(episodes):
        state = env.reset(initial_state={})
        done = False

        while not done:
            action = agent.act(state)
            next_state, reward, done, info = env.step(action, next_state=state)
            trajectory.append({"state": state, "action": action, "reward": reward})
            state = next_state

        agent.update(trajectory)
