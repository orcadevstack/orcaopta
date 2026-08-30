from pyspark.sql import SparkSession
from spark.pipelines import pipeline_utils

from spark.ingestion.log_ingest import create_spark, ingest_logs, union_all
from spark.processing.log_etl import parse_basic_fields, filter_noise
from spark.ingestion.telemetry_ingest import ingest_metrics
from spark.processing.telemetry_etl import normalize_metrics
from spark.analytics.sla_slo import compute_slo
from spark.anomaly.distributed_anomaly import zscore_anomaly

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
