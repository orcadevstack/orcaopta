
from kubernetes import client, config


def load_kube_config():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()


def audit_rbac():
    issues = []
    rbac = client.RbacAuthorizationV1Api()

    # ClusterRoles with wildcards
    for cr in rbac.list_cluster_role().items:
        for rule in cr.rules or []:
            if "*" in (rule.verbs or []) or "*" in (rule.resources or []):
                issues.append({
                    "severity": "high",
                    "resource": cr.metadata.name,
                    "type": "rbac_clusterrole_wildcard",
                    "message": f"ClusterRole {cr.metadata.name} uses wildcard verbs/resources"
                })

    # ClusterRoleBindings to admin or risky service accounts
    for crb in rbac.list_cluster_role_binding().items:
        for subj in crb.subjects or []:
            if subj.kind == "User" and subj.name == "system:admin":
                issues.append({
                    "severity": "high",
                    "resource": crb.metadata.name,
                    "type": "rbac_clusterrolebinding_admin",
                    "message": f"ClusterRoleBinding {crb.metadata.name} binds to system:admin"
                })
            if subj.kind == "ServiceAccount":
                issues.append({
                    "severity": "medium",
                    "resource": crb.metadata.name,
                    "type": "rbac_clusterrolebinding_sa",
                    "message": f"ClusterRoleBinding {crb.metadata.name} binds to SA {subj.name} in {subj.namespace}"
                })

    return issues


def audit_podsecurity():
    issues = []
    core = client.CoreV1Api()

    for ns in core.list_namespace().items:
        labels = ns.metadata.labels or {}
        has_psa = any(k.startswith("pod-security.kubernetes.io/") for k in labels)
        if not has_psa:
            issues.append({
                "severity": "medium",
                "resource": ns.metadata.name,
                "type": "podsecurity_namespace_no_psa",
                "message": f"Namespace {ns.metadata.name} has no PodSecurity labels"
            })

    return issues


def audit_network_policies():
    issues = []
    core = client.CoreV1Api()
    net = client.NetworkingV1Api()

    for ns in core.list_namespace().items:
        nps = net.list_namespaced_network_policy(ns.metadata.name).items
        if len(nps) == 0:
            issues.append({
                "severity": "medium",
                "resource": ns.metadata.name,
                "type": "networkpolicy_namespace_no_np",
                "message": f"Namespace {ns.metadata.name} has NO NetworkPolicies"
            })

    return issues


def audit_kubernetes_config():
    load_kube_config()
    return {
        "rbac": audit_rbac(),
        "podsecurity": audit_podsecurity(),
        "networkpolicies": audit_network_policies(),
    }


# ============================================================
# REMEDIATION SECTION
# ============================================================

def tighten_rbac():
    """
    Replace wildcard ClusterRoles with least-privilege versions.
    """
    rbac = client.RbacAuthorizationV1Api()
    fixed = []

    for cr in rbac.list_cluster_role().items:
        new_rules = []
        changed = False

        for rule in cr.rules or []:
            if "*" in (rule.verbs or []) or "*" in (rule.resources or []):
                changed = True
                new_rules.append(client.V1PolicyRule(
                    verbs=["get", "list", "watch"],
                    resources=["pods", "services", "deployments"]
                ))
            else:
                new_rules.append(rule)

        if changed:
            cr.rules = new_rules
            rbac.replace_cluster_role(cr.metadata.name, cr)
            fixed.append(cr.metadata.name)

    return fixed


def add_podsecurity_labels(namespace, level="restricted"):
    """
    Add PodSecurity labels to a namespace.
    """
    core = client.CoreV1Api()
    body = {
        "metadata": {
            "labels": {
                "pod-security.kubernetes.io/enforce": level,
                "pod-security.kubernetes.io/audit": level,
                "pod-security.kubernetes.io/warn": level,
            }
        }
    }
    core.patch_namespace(namespace, body)
    return f"Added PodSecurity labels to {namespace}"


def create_default_network_policy(namespace):
    """
    Create a deny-all NetworkPolicy for a namespace.
    """
    net = client.NetworkingV1Api()

    np = client.V1NetworkPolicy(
        metadata=client.V1ObjectMeta(name="default-deny"),
        spec=client.V1NetworkPolicySpec(
            pod_selector=client.V1LabelSelector(match_labels={}),
            policy_types=["Ingress", "Egress"],
            ingress=[],
            egress=[]
        )
    )

    net.create_namespaced_network_policy(namespace, np)
    return f"Created default deny-all NetworkPolicy in {namespace}"


def execute_kubernetes_plan(plan: str):
    """
    Parse AI plan and execute Kubernetes remediation actions.
    """
    load_kube_config()
    core = client.CoreV1Api()

    if "tighten rbac" in plan.lower():
        print("Tightening RBAC...")
        print(tighten_rbac())

    if "add podsecurity" in plan.lower():
        for ns in core.list_namespace().items:
            print(add_podsecurity_labels(ns.metadata.name))

    if "create networkpolicy" in plan.lower() or "default deny" in plan.lower():
        for ns in core.list_namespace().items:
            print(create_default_network_policy(ns.metadata.name))
