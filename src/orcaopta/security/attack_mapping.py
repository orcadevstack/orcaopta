import logging
from typing import List, Dict, Any

try:
    from attackcti import attack_client
except Exception:
    attack_client = None

logger = logging.getLogger("orcaopta.security.attack")


class AttackKnowledgeBase:
    def __init__(self):
        self.client = None
        self.techniques = {}
        self.tactics = {}

        if attack_client is None:
            logger.warning("attackcti not available; ATT&CK integration disabled.")
            return

        try:
            self.client = attack_client()
            self._load_techniques()
        except Exception as e:
            logger.warning(f"Failed to initialize ATT&CK client: {e}")
            self.client = None

    def _load_techniques(self):
        """
        Load enterprise ATT&CK techniques into memory.
        """
        enterprise_techniques = self.client.get_techniques()
        for t in enterprise_techniques:
            self.techniques[t["external_references"][0]["external_id"]] = t

        logger.info(f"Loaded {len(self.techniques)} ATT&CK techniques.")

    def get_technique(self, technique_id: str) -> Dict[str, Any]:
        return self.techniques.get(technique_id, {})


_attack_kb = AttackKnowledgeBase()


def _map_openstack_issue_to_attack(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example mapping: OpenStack security issue -> ATT&CK technique.
    You can expand this with real logic later.
    """
    desc = issue.get("description", "").lower()

    # Very simple heuristic examples:
    if "public" in desc and "network" in desc:
        technique_id = "T1046"  # Network Service Discovery
    elif "weak password" in desc or "default credential" in desc:
        technique_id = "T1078"  # Valid Accounts
    else:
        technique_id = "T1082"  # System Information Discovery (generic)

    technique = _attack_kb.get_technique(technique_id)

    return {
        "component": "openstack",
        "issue": issue,
        "technique_id": technique_id,
        "technique_name": technique.get("name", "Unknown"),
        "technique_description": technique.get("description", ""),
    }


def _map_terraform_issue_to_attack(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example mapping: Terraform misconfig -> ATT&CK technique.
    """
    msg = issue.get("message", "").lower()

    if "public" in msg or "0.0.0.0/0" in msg:
        technique_id = "T1190"  # Exploit Public-Facing Application
    elif "unencrypted" in msg or "no encryption" in msg:
        technique_id = "T1557"  # Man-in-the-Middle (as a proxy for weak transport)
    else:
        technique_id = "T1082"

    technique = _attack_kb.get_technique(technique_id)

    return {
        "component": "terraform",
        "issue": issue,
        "technique_id": technique_id,
        "technique_name": technique.get("name", "Unknown"),
        "technique_description": technique.get("description", ""),
    }


def analyze_cloud_graph(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Main entry point: take Orcaopta cloud_graph and return
    ATT&CK‑mapped security issues.
    """
    findings: List[Dict[str, Any]] = []

    # OpenStack network/storage issues
    openstack = graph.get("openstack", {})
    os_issues = openstack.get("issues", []) or openstack.get("security_issues", [])
    for issue in os_issues:
        findings.append(_map_openstack_issue_to_attack(issue))

    # Terraform issues
    tf = graph.get("terraform", {})
    tf_issues = tf.get("issues", [])
    for issue in tf_issues:
        findings.append(_map_terraform_issue_to_attack(issue))

    # You can add Kubernetes, Ceph, Spark, etc. here later.

    return findings
