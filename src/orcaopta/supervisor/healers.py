def heal(failure, state):
    if failure == "ml_anomaly":
        return heal_ml_anomaly(state)

    if failure == "missing_nodes":
        return heal_missing_nodes(state)

    if failure == "openstack_network":
        return heal_openstack_network(state)

    if failure == "kubernetes_config":
        return heal_kubernetes_config(state)

    return "unknown failure"


def heal_ml_anomaly(state):
    # Example: restart service, scale up, or trigger RL agent
    return "ML anomaly healed via autoscaling + RL agent"


def heal_missing_nodes(state):
    # Example: rebuild cloud graph, restart discovery
    return "Cloud graph rebuilt"


def heal_openstack_network(state):
    # Example: restart neutron agent, reapply security groups
    return "OpenStack network healing applied"


def heal_kubernetes_config(state):
    # Example: fix invalid config, restart pods
    return "Kubernetes config healing applied"
