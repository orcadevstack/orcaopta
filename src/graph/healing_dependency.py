import networkx as nx
from pyvis.network import Network

def render_healing_dependency(events, output_html="healing_dependency.html"):
    g = nx.DiGraph()

    for ev in events:
        issue = f"issue:{ev['issue_id']}"
        action = f"action:{ev['action_id']}"

        g.add_node(issue, type="issue")
        g.add_node(action, type="action")

        g.add_edge(issue, action, relation="triggers")

        # If action depends on other actions
        deps = ev.get("details", {}).get("depends_on", [])
        for d in deps:
            dep_action = f"action:{d}"
            g.add_edge(dep_action, action, relation="depends_on")

    net = Network(height="700px", width="100%", bgcolor="#000", font_color="white")
    net.barnes_hut()

    for node, attrs in g.nodes(data=True):
        color = "#d62728" if attrs["type"] == "issue" else "#2ca02c"
        net.add_node(node, label=node, title=str(attrs), color=color)

    for src, dst, attrs in g.edges(data=True):
        net.add_edge(src, dst, title=attrs.get("relation", ""))

    net.show(output_html)
    return output_html
