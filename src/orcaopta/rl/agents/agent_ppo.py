import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from orcaopta.tracking.client import OrcaoptaTracker
from src.orcaopta.rl.envs.autoscale_env import AutoscaleEnv

tracker = OrcaoptaTracker()


class PolicyNet(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, x):
        return self.net(x)


class ValueNet(nn.Module):
    def __init__(self, state_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.net(x)


class PPOAgent:
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, clip=0.2):
        self.policy = PolicyNet(state_dim, action_dim)
        self.value = ValueNet(state_dim)

        self.optimizer_policy = optim.Adam(self.policy.parameters(), lr=lr)
        self.optimizer_value = optim.Adam(self.value.parameters(), lr=lr)

        self.gamma = gamma
        self.clip = clip

    # -----------------------------------------------------
    # Action selection
    # -----------------------------------------------------
    def act(self, state):
        state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        logits = self.policy(state_t)
        probs = torch.softmax(logits, dim=-1)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action)

    # -----------------------------------------------------
    # Compute discounted returns
    # -----------------------------------------------------
    def compute_returns(self, rewards):
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        return torch.tensor(returns, dtype=torch.float32)

    # -----------------------------------------------------
    # PPO update step
    # -----------------------------------------------------
    def update(self, states, actions, log_probs_old, rewards):
        states_t = torch.tensor(states, dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.int64)
        returns_t = self.compute_returns(rewards)

        values = self.value(states_t).squeeze()
        advantages = returns_t - values.detach()

        logits = self.policy(states_t)
        probs = torch.softmax(logits, dim=-1)
        dist = torch.distributions.Categorical(probs)
        log_probs = dist.log_prob(actions_t)

        ratio = torch.exp(log_probs - log_probs_old)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip, 1 + self.clip) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()

        value_loss = (returns_t - values).pow(2).mean()

        self.optimizer_policy.zero_grad()
        policy_loss.backward()
        self.optimizer_policy.step()

        self.optimizer_value.zero_grad()
        value_loss.backward()
        self.optimizer_value.step()

        return policy_loss.item(), value_loss.item()

    def save(self, path):
        torch.save({
            "policy": self.policy.state_dict(),
            "value": self.value.state_dict()
        }, path)

    def load(self, path):
        checkpoint = torch.load(path)
        self.policy.load_state_dict(checkpoint["policy"])
        self.value.load_state_dict(checkpoint["value"])



def train_autoscale_rl(episodes=500):
    env = AutoscaleEnv()
    state_dim = len(env.reset())
    action_dim = 3  # scale_down, hold, scale_up

    agent = PPOAgent(state_dim, action_dim)

    for episode in range(episodes):
        state = env.reset()

        states = []
        actions = []
        rewards = []
        log_probs = []

        done = False

        while not done:
            action, log_prob = agent.act(state)
            next_state, reward, done, _ = env.step(action)

            states.append(state)
            actions.append(action)
            rewards.append(reward)
            log_probs.append(log_prob.detach())

            state = next_state

        # Update PPO
        policy_loss, value_loss = agent.update(
            states,
            actions,
            torch.stack(log_probs),
            rewards
        )

        # Log RL episode to OTS
        tracker.log_metric("rl_autoscale_reward", sum(rewards), {"episode": episode})
        tracker.log_event("rl_autoscale_episode", "rl", {
            "episode": episode,
            "reward": float(sum(rewards)),
            "policy_loss": policy_loss,
            "value_loss": value_loss
        })

        print(f"Episode {episode} | Reward: {sum(rewards):.3f} | Policy: {policy_loss:.3f} | Value: {value_loss:.3f}")

    return agent
