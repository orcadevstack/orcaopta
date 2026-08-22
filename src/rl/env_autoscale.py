import numpy as np

class AutoscaleEnv:
    """
    Simple RL environment for autoscaling decisions.
    State: [cpu_usage, requests, latency, replicas]
    Actions: 0=scale_down, 1=hold, 2=scale_up
    Reward: balance latency vs cost.
    """

    def __init__(self, max_replicas=20):
        self.max_replicas = max_replicas
        self.min_replicas = 1
        self.reset()

    def reset(self):
        self.cpu_usage = 0.6
        self.requests = 100
        self.latency = 200  # ms
        self.replicas = 3
        self.step_count = 0
        return self._get_state()

    def _get_state(self):
        return np.array([
            self.cpu_usage,
            self.requests / 1000.0,
            self.latency / 1000.0,
            self.replicas / self.max_replicas
        ], dtype=np.float32)

    def step(self, action: int):
        # Apply action
        if action == 0:  # scale_down
            self.replicas = max(self.min_replicas, self.replicas - 1)
        elif action == 2:  # scale_up
            self.replicas = min(self.max_replicas, self.replicas + 1)

        # Simulate workload change
        self.requests += np.random.randint(-20, 20)
        self.requests = max(10, self.requests)

        # Simulate CPU & latency based on replicas
        load_per_replica = self.requests / self.replicas
        self.cpu_usage = min(1.0, load_per_replica / 200.0)
        self.latency = max(50, 300 * self.cpu_usage)

        # Reward: low latency, low cost
        cost = self.replicas
        perf_penalty = self.latency / 1000.0
        reward = - (0.7 * perf_penalty + 0.3 * cost / self.max_replicas)

        self.step_count += 1
        done = self.step_count >= 100

        return self._get_state(), reward, done, {}
