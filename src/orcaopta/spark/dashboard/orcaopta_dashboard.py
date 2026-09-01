import streamlit as st
import pandas as pd
import altair as alt
from pyspark.sql import SparkSession

# ---------------------------------------------------------
# Spark session
# ---------------------------------------------------------
def get_spark():
    return (
        SparkSession.builder
        .appName("OrcaoptaDashboard")
        .getOrCreate()
    )

def load_table(spark, path: str):
    return spark.read.parquet(path).toPandas()


# ---------------------------------------------------------
# UI Layout
# ---------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Orcaopta SRE Dashboard",
        page_icon="🛰️",
        layout="wide"
    )

    st.title("🛰️ Orcaopta Enterprise SRE Analytics Dashboard")
    st.markdown("### Real‑time Observability • Incident Prediction • Root‑Cause Analysis • Self‑Healing")

    spark = get_spark()

    # Sidebar
    st.sidebar.header("📡 Data Sources")
    slo_path = st.sidebar.text_input("SLO Data", "s3a://orca/analytics/slo/")
    anomalies_path = st.sidebar.text_input("Anomalies", "s3a://orca/analytics/anomalies/")
    incidents_path = st.sidebar.text_input("Incidents", "s3a://orca/analytics/incidents/")
    correlation_path = st.sidebar.text_input("Correlation", "s3a://orca/analytics/correlation/")
    rca_path = st.sidebar.text_input("Root Cause", "s3a://orca/analytics/rca/")
    remediation_path = st.sidebar.text_input("Remediation", "s3a://orca/analytics/remediation/")
    forecast_path = st.sidebar.text_input("Forecast", "s3a://orca/analytics/forecast/")

    auto_refresh = st.sidebar.checkbox("Auto‑refresh every 10 seconds")

    if st.sidebar.button("Load Data"):
        slo_df = load_table(spark, slo_path)
        anomalies_df = load_table(spark, anomalies_path)
        incidents_df = load_table(spark, incidents_path)
        correlation_df = load_table(spark, correlation_path)
        rca_df = load_table(spark, rca_path)
        remediation_df = load_table(spark, remediation_path)
        forecast_df = load_table(spark, forecast_path)

        # ---------------------------------------------------------
        # KPI Row
        # ---------------------------------------------------------
        st.markdown("## 📊 Key SRE Indicators")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("SLO Error Rate", f"{slo_df['error_rate'].iloc[0]:.2%}")
        col2.metric("Total Incidents", len(incidents_df))
        col3.metric("Active Anomalies", anomalies_df['anomaly'].sum())
        col4.metric("Drift Signals", correlation_df['drift_signal'].sum())

        # ---------------------------------------------------------
        # Tabs
        # ---------------------------------------------------------
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 SLO & Latency",
            "⚠️ Anomalies",
            "🔥 Incident Predictions",
            "🧠 Root‑Cause Analysis",
            "🔧 Remediation Actions",
            "📡 Forecasting"
        ])

        # ---------------------------------------------------------
        # Tab 1: SLO & Latency
        # ---------------------------------------------------------
        with tab1:
            st.subheader("SLO Trends")
            slo_chart = alt.Chart(slo_df).mark_line().encode(
                x="timestamp:T",
                y="error_rate:Q",
                color=alt.value("#FF4B4B")
            )
            st.altair_chart(slo_chart, use_container_width=True)

            st.subheader("Latency Distribution")
            if "avg_latency" in correlation_df.columns:
                latency_chart = alt.Chart(correlation_df).mark_bar().encode(
                    x="avg_latency:Q",
                    y="count()"
                )
                st.altair_chart(latency_chart, use_container_width=True)

        # ---------------------------------------------------------
        # Tab 2: Anomalies
        # ---------------------------------------------------------
        with tab2:
            st.subheader("Anomaly Timeline")
            anomaly_chart = alt.Chart(anomalies_df).mark_circle(size=60).encode(
                x="timestamp:T",
                y="value:Q",
                color="anomaly:N",
                tooltip=["source", "metric_name", "value"]
            )
            st.altair_chart(anomaly_chart, use_container_width=True)

            st.write("### Raw Anomaly Data")
            st.dataframe(anomalies_df)

        # ---------------------------------------------------------
        # Tab 3: Incident Predictions
        # ---------------------------------------------------------
        with tab3:
            st.subheader("Incident Risk Levels")
            st.dataframe(incidents_df)

            risk_chart = alt.Chart(incidents_df).mark_bar().encode(
                x="incident_prediction:N",
                y="count()",
                color="incident_prediction:N"
            )
            st.altair_chart(risk_chart, use_container_width=True)

        # ---------------------------------------------------------
        # Tab 4: Root‑Cause Analysis
        # ---------------------------------------------------------
        with tab4:
            st.subheader("Root‑Cause Ranking")
            st.dataframe(rca_df.sort_values("root_cause_score", ascending=False))

            rca_chart = alt.Chart(rca_df).mark_bar().encode(
                x="id:N",
                y="root_cause_score:Q",
                color="root_cause_level:N"
            )
            st.altair_chart(rca_chart, use_container_width=True)

        # ---------------------------------------------------------
        # Tab 5: Remediation Actions
        # ---------------------------------------------------------
        with tab5:
            st.subheader("Self‑Healing Actions")
            st.dataframe(remediation_df)

            action_chart = alt.Chart(remediation_df).mark_bar().encode(
                x="action:N",
                y="count()",
                color="remediation_type:N"
            )
            st.altair_chart(action_chart, use_container_width=True)

        # ---------------------------------------------------------
        # Tab 6: Forecasting
        # ---------------------------------------------------------
        with tab6:
            st.subheader("Resource Forecast")
            forecast_chart = alt.Chart(forecast_df).mark_line().encode(
                x="ts_numeric:Q",
                y="prediction:Q",
                color=alt.value("#00AEEF")
            )
            st.altair_chart(forecast_chart, use_container_width=True)

            st.dataframe(forecast_df)

    if auto_refresh:
        st.experimental_rerun()


if __name__ == "__main__":
    main()
