from pyspark.sql import SparkSession

from src.spark.ingestion.log_ingest import ingest_logs, union_all
from src.spark.processing.log_etl import parse_basic_fields, filter_noise
from src.spark.ingestion.telemetry_ingest import ingest_metrics
from src.spark.processing.telemetry_etl import normalize_metrics

from src.spark.analytics.sla_slo import compute_slo
from src.spark.analytics.failure_patterns import detect_failure_patterns
from src.spark.analytics.resource_forecasting import forecast_resource_usage
from src.spark.analytics.cluster_behavior import cluster_behavior

from src.spark.anomaly.distributed_anomaly import detect_anomalies
from src.spark.anomaly.drift_detection import page_hinkley_drift

from src.spark.correlation.event_correlation import enterprise_event_correlation
from src.spark.correlation.incident_prediction import predict_incidents
from src.spark.correlation.remediation_graph import build_remediation_graph
from src.orcaopta.controller.self_healing_controller import run_self_healing

import json
import os


def create_spark():
    return (
        SparkSession.builder
        .appName("OrcaoptaSREBatchPipeline")
        .getOrCreate()
    )


def load_config(path: str = "spark_config.json") -> dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def run_sre_batch():
    spark = create_spark()
    config = load_config()

    log_sources = config.get("log_sources", {})
    metrics_path = config.get("metrics_path")

    # 1. Ingest
    logs_frames = ingest_logs(spark, log_sources)
    logs = union_all(logs_frames)
    logs = parse_basic_fields(logs)
    logs = filter_noise(logs)

    metrics = ingest_metrics(spark, metrics_path)
    metrics = normalize_metrics(metrics)

    # 2. Analytics
    slo = compute_slo(logs)
    failure_patterns = detect_failure_patterns(logs)
    forecast = forecast_resource_usage(metrics)
    behavior = cluster_behavior(metrics)

    # 3. Anomalies + drift
    anomalies = detect_anomalies(metrics, "cpu_usage")
    drift = page_hinkley_drift(metrics, "cpu_usage")

    # 4. Correlation
    correlation = enterprise_event_correlation(logs, metrics, anomalies, drift)

    # 5. Incident prediction
    incidents = predict_incidents(correlation, anomalies, drift)

    # 6. Remediation graph
    remediation_df = build_remediation_graph(incidents)

    # 7. Self‑healing
    run_self_healing(remediation_df)

    print("=== SLO ===", slo)
    print("=== Failure Patterns ===")
    failure_patterns.show(20, truncate=False)
    print("=== Forecast ===")
    if forecast is not None:
        forecast.show(20, truncate=False)
    print("=== Cluster Behavior ===")
    behavior.show(20, truncate=False)
    print("=== Correlation ===")
    correlation.show(20, truncate=False)
    print("=== Incidents ===")
    incidents.show(20, truncate=False)
    print("=== Remediation ===")
    remediation_df.show(20, truncate=False)

    return {
        "slo": slo,
        "failure_patterns": failure_patterns,
        "forecast": forecast,
        "behavior": behavior,
        "correlation": correlation,
        "incidents": incidents,
        "remediation": remediation_df,
    }


if __name__ == "__main__":
    run_sre_batch()
