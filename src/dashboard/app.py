import streamlit as st
import requests

API_BASE = "http://localhost:8000"   # your FastAPI URL

st.set_page_config(page_title="Orcaopta Dashboard", layout="wide")

st.title("🧠 ORCAOPTA Cloud Brain Dashboard")


# ============================
# CLOUD GRAPH VIEW
# ============================

st.header("🌐 Unified Cloud Graph")

if st.button("Refresh Cloud Graph"):
    graph = requests.get(f"{API_BASE}/dashboard/cloud-graph").json()["graph"]
    st.json(graph)


# ============================
# HEALING EVENTS VIEW
# ============================

st.header("⚡ Healing Events Timeline")

if st.button("Refresh Healing Events"):
    events = requests.get(f"{API_BASE}/dashboard/healing-events").json()["events"]
    for event in events:
        st.subheader(f"{event['timestamp']} — {event['kind']}")
        st.json(event["details"])


# ============================
# GLOBAL SELF-HEAL PLAN
# ============================

st.header("🩺 Global Self-Heal Plan")

if st.button("Generate Global Healing Plan"):
    plan = requests.get(f"{API_BASE}/ai/global-self-heal").json()["global_self_heal_plan"]
    st.code(plan)
