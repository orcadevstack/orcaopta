
from pyvis.network import Network
import networkx as nx

from src.graph.themes import THEMES, heat_color


def render_pyvis_graph(
    nx_graph: nx.DiGraph,
    theme: str = "dark",
    output_html: str = "cloud_graph.html",
    use_heatmap: bool = True,
):
    t = THEMES.get(theme, THEMES["dark"])

    net = Network(height="800px", width="100%", bgcolor=t["bg"], font_color=t["font"])
    net.barnes_hut()

    for node, attrs in nx_graph.nodes(data=True):
        node_type = attrs.get("type", "default")
        base_color = t.get(node_type, t["default"])

        if use_heatmap:
            load = float(attrs.get("load", 0.0))
            color = heat_color(load)
        else:
            color = base_color

        net.add_node(
            node,
            label=attrs.get("label", node),
            title=str(attrs),
            color=color,
            group=attrs.get("group"),
        )

    for src, dst, attrs in nx_graph.edges(data=True):
        net.add_edge(src, dst, title=attrs.get("relation", ""))

    net.show(output_html)
    return output_html
