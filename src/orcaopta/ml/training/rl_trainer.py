"""
RL training orchestration: wires envs + agents + training loops.
"""

from orcaopta.ml.rl.envs.autoscale_env import AutoscaleEnv
from orcaopta.ml.rl.envs.anomaly_env import AnomalyEnv
from orcaopta.ml.rl.envs.resource_env import ResourceEnv
from orcaopta.ml.rl.agents.ppo_agent import PPOAgent
from orcaopta.ml.rl.agents.dqn_agent import DQNAgent
from orcaopta.ml.rl.training.autoscale_train import train_autoscale
from orcaopta.ml.rl.training.anomaly_train import train_anomaly
from orcaopta.ml.rl.training.resource_train import train_resource


class RLTrainer:
    def __init__(self) -> None:
        self.autoscale_env = AutoscaleEnv()
        self.anomaly_env = AnomalyEnv()
        self.resource_env = ResourceEnv()

        self.ppo_agent = PPOAgent()
        self.dqn_agent = DQNAgent()

    def train_all(self) -> None:
        train_autoscale(self.autoscale_env, self.ppo_agent)
        train_anomaly(self.anomaly_env, self.dqn_agent)
        train_resource(self.resource_env, self.ppo_agent)
