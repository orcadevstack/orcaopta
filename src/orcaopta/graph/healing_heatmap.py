import networkx as nx
from pyvis.network import Network

def severity_to_heat(severity: str) -> float:
    """
    Convert severity → heat value (0.0 to 1.0)
    """
    mapping = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
        "critical": 1.0,
    }
    return mapping.get(severity.lower(), 0.3)


def heat_color(value: float) -> str:
    """
    Heatmap color: green → yellow → red
    """
    v = max(0.0, min(1.0, value))
    r = int(255 * v)
    g = int(255 * (1.0 - v))
    return f"#{r:02x}{g:02x}00"


def render_healing_heatmap(events: list[dict], output_html="healing_heatmap.html"):
    g = nx.DiGraph()

    for ev in events:
        issue = f"issue:{ev['issue_id']}"
        heat = severity_to_heat(ev.get("severity", "medium"))

        g.add_node(issue, severity=ev.get("severity"), heat=heat)

    net = Network(height="600px", width="100%", bgcolor="#000", font_color="white")
    net.barnes_hut()

    for node, attrs in g.nodes(data=True):
        color = heat_color(attrs["heat"])
        net.add_node(node, label=node, title=str(attrs), color=color)

    net.show(output_html)
    return output_html
