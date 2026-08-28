
from pyvis.network import Network
from .engine import OrcaGraphEngine

def render_cloud_topology(engine: OrcaGraphEngine, output_html: str = "cloud_topology.html"):
    net = Network(height="800px", width="100%", bgcolor="#111", font_color="white")
    net.barnes_hut()

    for node, attrs in engine.graph.nodes(data=True):
        net.add_node(
            node,
            label=attrs.get("name", node),
            title=str(attrs),
            color=_color_for_type(attrs.get("type"))
        )

    for src, dst, attrs in engine.graph.edges(data=True):
        net.add_edge(src, dst, title=attrs.get("relation", ""))

    net.show(output_html)

def _color_for_type(t: str) -> str:
    return {
        "project": "#1f77b4",
        "vm": "#ff7f0e",
        "volume": "#2ca02c",
        "pod": "#d62728",
        "service": "#9467bd",
    }.get(t, "#7f7f7f")
