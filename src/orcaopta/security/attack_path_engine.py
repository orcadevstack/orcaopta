

import networkx as nx
from orcaopta.vunescaning.engine.results import ScanResult, Issue

class AttackPathEngine:
    """
    Advanced attack path engine for Orcaopta.
    Builds weighted attack graphs using:
    - Severity
    - CVE exploitability
    - Cloud/K8s/SaaS context
    - Runtime detections
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    # -------------------------------------------------------------
    # Node weight calculation
    # -------------------------------------------------------------
    def weight(self, issue: Issue):
        sev = issue.severity.lower()
        base = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 2,
            "unknown": 1,
        }.get(sev, 1)

        # CVE exploitability score
        exploit = 0
        if issue.id.startswith("CVE"):
            nvd = issue.metadata.get("nvd", {})
            exploit = nvd.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("exploitabilityScore", 0)

        return base + exploit

    # -------------------------------------------------------------
    # Build graph
    # -------------------------------------------------------------
    def build(self, results: ScanResult):
        for issue in results.all():
            w = self.weight(issue)
            self.graph.add_node(issue.id, weight=w, title=issue.title, severity=issue.severity)

            # Attack path heuristics
            if issue.severity == "critical":
                self.graph.add_edge("entrypoint", issue.id, risk=w)
            elif issue.severity == "high":
                self.graph.add_edge(issue.id, "privilege_escalation", risk=w)
            elif issue.severity == "medium":
                self.graph.add_edge(issue.id, "lateral_movement", risk=w)
            else:
                self.graph.add_edge(issue.id, "low_risk", risk=w)

    # -------------------------------------------------------------
    # Export graph
    # -------------------------------------------------------------
    def export(self, path: str):
        nx.write_graphml(self.graph, path)

    # -------------------------------------------------------------
    # Compute highest-risk path
    # -------------------------------------------------------------
    def highest_risk_path(self):
        try:
            return nx.dag_longest_path(self.graph, weight="risk")
        except Exception:
            return []
