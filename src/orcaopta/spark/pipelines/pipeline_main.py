from pyspark.sql import SparkSession
from orcaopta.spark.pipelines import pipeline_utils

from orcaopta.spark.ingestion.log_ingest import create_spark, ingest_logs, union_all
from orcaopta.spark.processing.log_etl import parse_basic_fields, filter_noise
from orcaopta.spark.ingestion.telemetry_ingest import ingest_metrics
from orcaopta.spark.processing.telemetry_etl import normalize_metrics
from orcaopta.spark.analytics.sla_slo import compute_slo
from orcaopta.spark.anomaly.distributed_anomaly import zscore_anomaly

def run_pipeline(config: dict):
    spark = create_spark("OrcaoptaSparkPipeline")

    log_sources = config.get("log_sources", {})
    metrics_path = config.get("metrics_path")

    logs_frames = ingest_logs(spark, log_sources)
    logs = union_all(logs_frames)
    logs = parse_basic_fields(logs)
    logs = filter_noise(logs)

    metrics = ingest_metrics(spark, metrics_path)
    metrics = normalize_metrics(metrics)

    slo = compute_slo(logs)
    anomalies = zscore_anomaly(metrics)

    return {
        "slo": slo,
        "anomalies_df": anomalies,
    }
