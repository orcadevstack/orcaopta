# src/dashboard/graph_module.py
import streamlit as st

from src.graph.engine import OrcaGraphEngine
from src.graph.pyvis_renderer import render_pyvis_graph
from src.graph.healing_graph import render_healing_graph
from src.graph.architecture import generate_architecture_diagram


def show_cloud_graph(cloud_graph_json: dict, theme: str = "dark"):
    st.subheader("Interactive Cloud Graph")

    engine = OrcaGraphEngine()
    engine.load_from_api(cloud_graph_json)

    html_file = render_pyvis_graph(engine.graph, theme=theme)

    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=800, scrolling=True)


def show_healing_graph(events_json: dict):
    st.subheader("Healing Graph")

    html_file = render_healing_graph(events_json["events"])

    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=600, scrolling=True)


def show_architecture_diagram():
    st.subheader("Architecture Diagram")

    generate_architecture_diagram()
    st.image("orcaopta_architecture.png")
