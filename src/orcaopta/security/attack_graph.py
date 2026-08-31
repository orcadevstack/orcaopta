
import networkx as nx
from orcaopta.vunescaning.engine.results import ScanResult

class AttackGraph:
    """
    Builds an attack graph from vulnerabilities.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build(self, results: ScanResult):
        for issue in results.all():
            sev = issue.severity.lower()

            # Node = vulnerability
            self.graph.add_node(issue.id, severity=sev, title=issue.title)

            # Simple heuristic: critical → high → medium → low
            if sev == "critical":
                self.graph.add_edge("entrypoint", issue.id)
            elif sev == "high":
                self.graph.add_edge(issue.id, "privilege_escalation")
            elif sev == "medium":
                self.graph.add_edge(issue.id, "lateral_movement")
            else:
                self.graph.add_edge(issue.id, "low_risk")

    def export(self, path: str):
        nx.write_graphml(self.graph, path)
