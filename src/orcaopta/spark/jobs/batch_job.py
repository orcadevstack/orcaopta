from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# Import your pipeline modules
from orcaopta.spark.ingestion.log_ingest import ingest_logs, union_all
from orcaopta.spark.processing.log_etl import parse_basic_fields, filter_noise
from orcaopta.spark.ingestion.telemetry_ingest import ingest_metrics
from orcaopta.spark.processing.telemetry_etl import normalize_metrics
from orcaopta.spark.analytics.sla_slo import compute_slo
from orcaopta.spark.analytics.resource_forecasting import forecast_resource_usage
from orcaopta.spark.anomaly.distributed_anomaly import zscore_anomaly
from orcaopta.spark.correlation.event_correlation import correlate_events
from orcaopta.spark.anomaly.feature_engineering import build_features
from orcaopta.spark.anomaly.distributed_anomaly import detect_anomalies
from orcaopta.spark.correlation.incident_prediction import predict_incidents

import json
import os

features = build_features(metrics, "cpu_usage")
features.show(20, truncate=False)

print("Running distributed anomaly detection...")
anomalies = detect_anomalies(metrics, "cpu_usage")
anomalies.show(50, truncate=False)

incidents = predict_incidents(correlation, anomalies, drift)
incidents.show(50, truncate=False)

def create_spark(app_name="OrcaoptaBatchJob"):
    return (
        SparkSession.builder
        .appName(app_name)
        .getOrCreate()
    )


def load_config(path="spark_config.json"):
    if not os.path.exists(path):
        print("No config file found, using defaults.")
        return {}

    with open(path) as f:
        return json.load(f)


def run_batch():
    # 1. Spark session
    spark = create_spark()

    # 2. Load config
    config = load_config()

    log_sources = config.get("log_sources", {})
    metrics_path = config.get("metrics_path")
    drift_baseline = config.get("drift_baseline", {})

    print("=== Starting Orcaopta Batch Job ===")

    # 3. Ingest logs
    print("Ingesting logs...")
    logs_frames = ingest_logs(spark, log_sources)
    logs = union_all(logs_frames)

    # 4. ETL logs
    logs = parse_basic_fields(logs)
    logs = filter_noise(logs)

    # 5. Ingest metrics
    print("Ingesting telemetry metrics...")
    metrics = ingest_metrics(spark, metrics_path)

    # 6. ETL metrics
    metrics = normalize_metrics(metrics)

    # 7. Compute SLO/SLA analytics
    print("Computing SLO/SLA...")
    slo = compute_slo(logs)
    print("SLO:", slo)

    # 8. Forecast resource usage
    print("Forecasting resource usage...")
    forecast = forecast_resource_usage(metrics)
    print("Forecast:", forecast)

    # 9. Distributed anomaly detection
    print("Running anomaly detection...")
    anomalies = zscore_anomaly(metrics)
    anomalies.show(20, truncate=False)

    # 10. Drift detection (batch version)
    print("Running drift detection...")
    drift = metrics.withColumn(
        "drift",
        col("value") - col("baseline")
    ).withColumn(
        "is_drift",
        (col("drift").abs() > 10)
    )
    drift.show(20, truncate=False)

    # 11. Event correlation
    print("Correlating events...")
    correlation = correlate_events(logs, metrics)
    correlation.show(20, truncate=False)

    print("=== Batch Job Completed ===")

    return {
        "slo": slo,
        "forecast": forecast,
        "anomalies": anomalies,
        "drift": drift,
        "correlation": correlation,
    }


if __name__ == "__main__":
    run_batch()
