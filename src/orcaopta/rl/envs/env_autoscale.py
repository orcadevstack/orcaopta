import numpy as np
from orcaopta.cloud.detect.graph import build_cloud_graph
from src.ml import autoscaling
from orcaopta.tracking.client import OrcaoptaTracker

tracker = OrcaoptaTracker()

class AutoscaleEnv:
    """
    RL environment for autoscaling decisions using Orcaopta's real cloud graph.

    State vector:
        [
            latency_norm,
            cost_norm,
            nodes_norm,
            cpu_norm,
            ram_norm,
            stability_norm
        ]

    Actions:
        0 = scale_down
        1 = hold
        2 = scale_up

    Reward:
        + Lower latency
        + Lower cost
        + Higher stability
    """

    def __init__(self, max_steps=200):
        self.max_steps = max_steps
        self.step_count = 0
        self.graph = None
        self.state = None


    def reset(self):
        self.step_count = 0
        self.graph = build_cloud_graph()
        self.state = self._extract_state(self.graph)
        return self.state

    def step(self, action: int):
        # Convert RL action → Orcaopta autoscaling decision
        decision = autoscaling.autoscale_decision_from_action(action)

        # Apply decision to cloud graph (real or simulated)
        new_graph = autoscaling.apply_decision(self.graph, decision)

        # Extract next state
        next_state = self._extract_state(new_graph)

        # Compute reward
        reward = self._compute_reward(self.graph, new_graph)

        # Log RL step into OTS
        tracker.log_event("rl_autoscale_step", "rl", {
            "action": action,
            "decision": decision,
            "reward": reward
        })

        # Update environment
        self.graph = new_graph
        self.state = next_state
        self.step_count += 1

        # Episode termination
        done = self.step_count >= self.max_steps

        return next_state, reward, done, {}

    def _extract_state(self, graph):
        """
        Convert Orcaopta cloud graph into RL-friendly numeric state.
        Missing keys are safely defaulted.
        """
        latency = graph.get("latency", 200) / 1000.0
        cost = graph.get("cost", 10) / 100.0
        nodes = graph.get("nodes", 3) / 50.0
        cpu = graph.get("cpu_usage", 0.5)
        ram = graph.get("ram_usage", 0.5)
        stability = graph.get("stability_score", 0.5)

        return np.array([
            latency,
            cost,
            nodes,
            cpu,
            ram,
            stability
        ], dtype=np.float32)

    def _compute_reward(self, old, new):
        """
        Reward based on improvements in latency, cost, and stability.
        """
        old_latency = old.get("latency", 200)
        new_latency = new.get("latency", 200)

        old_cost = old.get("cost", 10)
        new_cost = new.get("cost", 10)

        new_stability = new.get("stability_score", 0.5)

        reward = 0
        reward += (old_latency - new_latency) * 0.01      # latency improvement
        reward += (old_cost - new_cost) * 0.02            # cost reduction
        reward += new_stability * 0.5                     # stability bonus

        return reward
