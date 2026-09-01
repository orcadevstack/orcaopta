"""
Training loop for anomaly RL environment + agent.
"""

from typing import List, Dict
from orcaopta.ml.rl.envs.anomaly_env import AnomalyEnv
from orcaopta.ml.rl.agents.dqn_agent import DQNAgent


def train_anomaly(env: AnomalyEnv, agent: DQNAgent, episodes: int = 10) -> None:
    trajectory: List[Dict] = []

    for _ in range(episodes):
        state = env.reset(initial_state={"anomaly_score": 0.0})
        done = False

        while not done:
            action = agent.act(state)
            next_state, reward, done, info = env.step(action, next_state=state)
            trajectory.append({"state": state, "action": action, "reward": reward})
            state = next_state

        agent.update(trajectory)
