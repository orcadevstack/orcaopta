
from pyvis.network import Network
import networkx as nx

def build_healing_graph(events: list[dict]) -> nx.DiGraph:
    g = nx.DiGraph()
    for ev in events:
        issue_id = f"issue:{ev['issue_id']}"
        action_id = f"action:{ev['action_id']}"

        g.add_node(issue_id, type="issue", severity=ev.get("severity"))
        g.add_node(action_id, type="action", status=ev.get("status"))

        g.add_edge(issue_id, action_id, relation="healed_by")
    return g

def render_healing_graph(events: list[dict], output_html: str = "healing_graph.html"):
    g = build_healing_graph(events)
    net = Network(height="600px", width="100%", bgcolor="#000", font_color="white")
    net.barnes_hut()

    for node, attrs in g.nodes(data=True):
        net.add_node(
            node,
            label=node,
            title=str(attrs),
            color="#d62728" if attrs.get("type") == "issue" else "#2ca02c"
        )

    for src, dst, attrs in g.edges(data=True):
        net.add_edge(src, dst, title=attrs.get("relation", ""))

    net.show(output_html)
