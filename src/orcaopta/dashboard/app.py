# src/dashboard/app.py
import time
import json
import threading

import streamlit as st
import requests

from orcaopta.graph.engine import OrcaGraphEngine
from orcaopta.dashboard.graph_module import show_cloud_graph

from orcaopta.graph.healing_heatmap import render_healing_heatmap
from orcaopta.graph.healing_severity_gradient import render_healing_severity_gradient
from orcaopta.graph.healing_timeline import render_healing_timeline
from orcaopta.graph.healing_dependency import render_healing_dependency
from orcaopta.graph.healing_rl_reward import render_rl_reward_graph
from orcaopta.graph.architecture import generate_architecture_diagram

API_BASE = "http://localhost:8000"


st.set_page_config(page_title="Orcaopta Dashboard", layout="wide")
st.title("ORCAOPTA Cloud Brain Dashboard")


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to:",
    [
        "System Mode",
        "Healing Status",
        "Cloud Graph",
        "Healing Events & Graphs",
        "Self-Heal Plan",
        "Architecture Diagram",
    ],
)

theme = st.sidebar.selectbox("Theme", ["Dark", "Light"])
refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", 0, 30, 0)

if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #111111; color: white; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        body { background-color: #f5f5f5; color: black; }
        </style>
        """,
        unsafe_allow_html=True,
    )

if refresh_rate > 0:
    time.sleep(refresh_rate)
    st.experimental_rerun()


def fetch_json(endpoint: str):
    try:
        return requests.get(f"{API_BASE}{endpoint}").json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def status_badge(ok: bool):
    return " Available" if ok else " Missing"


if page == "System Mode":
    st.header("System Mode & Backends")

    mode_info = fetch_json("/system/mode")

    if mode_info:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Mode", mode_info["mode"])
        col2.metric("MLflow Backend", mode_info["mlflow_backend"])
        col3.metric("Database", mode_info["database_backend"])
        col4.metric("Queue", mode_info["queue_backend"])
        col5.metric("Storage", mode_info["storage_backend"])


if page == "Healing Status":
    st.header("🩺 Healing Subsystem Status")

    heal_status = fetch_json("/dashboard/heal-status")

    if heal_status:
        st.subheader(f"Current Mode: **{heal_status['mode']}**")

        colA, colB, colC, colD, colE = st.columns(5)
        colA.write(f"**Cloud Graph**: {status_badge(heal_status['cloud_graph'])}")
        colB.write(f"**OpenStack**: {status_badge(heal_status['openstack'])}")
        colC.write(f"**Kubernetes**: {status_badge(heal_status['kubernetes'])}")
        colD.write(f"**Terraform**: {status_badge(heal_status['terraform'])}")
        colE.write(f"**Ceph**: {status_badge(heal_status['ceph'])}")



if page == "Cloud Graph":
    st.header("Unified Cloud Graph")

    if st.button("Refresh Cloud Graph"):
        graph = fetch_json("/dashboard/cloud-graph")
        if graph:
            st.subheader("Raw Cloud Graph JSON")
            st.json(graph["graph"])

    st.subheader("Interactive Cloud Graph (PyVis)")

    if st.button("Visualize Cloud Graph"):
        graph = fetch_json("/dashboard/cloud-graph")
        if graph:
            show_cloud_graph(graph["graph"], theme="dark")



if page == "Healing Events & Graphs":
    st.header("Healing Events Timeline")

    events = fetch_json("/dashboard/healing-events")

    if events:
        for event in events["events"]:
            with st.expander(f"{event['timestamp']} — {event['kind']}"):
                st.json(event["details"])

        st.header("Healing Graph Visualizations")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "Heatmap",
                "Severity Gradient",
                "Timeline",
                "Dependency Graph",
                "RL Reward Graph",
            ]
        )

        with tab1:
            html = render_healing_heatmap(events["events"])
            st.components.v1.html(open(html).read(), height=600)

        with tab2:
            html = render_healing_severity_gradient(events["events"])
            st.components.v1.html(open(html).read(), height=600)

        with tab3:
            html = render_healing_timeline(events["events"])
            st.components.v1.html(open(html).read(), height=600)

        with tab4:
            html = render_healing_dependency(events["events"])
            st.components.v1.html(open(html).read(), height=700)

        with tab5:
            rewards_resp = fetch_json("/ai/rl/rewards")
            if rewards_resp and "rewards" in rewards_resp:
                html = render_rl_reward_graph(rewards_resp["rewards"])
                st.components.v1.html(open(html).read(), height=600)
            else:
                st.info("No RL rewards available yet.")
    else:
        st.info("No healing events found.")


if page == "Self-Heal Plan":
    st.header("Global Self-Heal Plan")

    if st.button("Generate Global Healing Plan"):
        plan = fetch_json("/ai/global-self-heal")
        if plan:
            st.code(plan["global_self_heal_plan"])



if page == "Architecture Diagram":
    st.header("Architecture Diagram")

    if st.button("Generate Architecture Diagram"):
        png_path = generate_architecture_diagram()
        st.image(png_path, caption="Orcaopta Architecture", use_column_width=True)
