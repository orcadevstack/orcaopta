import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

class PolicyNet(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x):
        return self.net(x)

class ValueNet(nn.Module):
    def __init__(self, state_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
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

    def act(self, state):
        state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        logits = self.policy(state_t)
        probs = torch.softmax(logits, dim=-1)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action)

    def compute_returns(self, rewards):
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        return torch.tensor(returns, dtype=torch.float32)

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
