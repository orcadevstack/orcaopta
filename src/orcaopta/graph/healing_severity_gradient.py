import networkx as nx
from pyvis.network import Network

GRADIENT = {
    "low": "#2ca02c",        # green
    "medium": "#ffbf00",     # amber
    "high": "#ff7f0e",       # orange
    "critical": "#d62728",   # red
}

def render_healing_severity_gradient(events, output_html="healing_severity_gradient.html"):
    g = nx.DiGraph()

    for ev in events:
        issue = f"issue:{ev['issue_id']}"
        severity = ev.get("severity", "medium").lower()
        g.add_node(issue, severity=severity)

    net = Network(height="600px", width="100%", bgcolor="#000", font_color="white")
    net.barnes_hut()

    for node, attrs in g.nodes(data=True):
        color = GRADIENT.get(attrs["severity"], "#7f7f7f")
        net.add_node(node, label=node, title=str(attrs), color=color)

    net.show(output_html)
    return output_html
