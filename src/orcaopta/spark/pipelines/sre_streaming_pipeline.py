from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from orcaopta.spark.jobs.streaming_job import create_streaming_session
from orcaopta.spark.anomaly.drift_detection import page_hinkley_drift
from orcaopta.spark.correlation.event_correlation import enterprise_event_correlation
from orcaopta.spark.correlation.incident_prediction import predict_incidents
from orcaopta.spark.correlation.remediation_graph import build_remediation_graph
from orcaopta.controller.self_healing_controller import run_self_healing


def run_sre_stream():
    spark = create_streaming_session()

    # Assume you already have a streaming metrics DataFrame `metrics_stream`
    # from Kafka (like in your streaming_job.py)
    # Here we just reference it as `metrics_stream`.

    # Example placeholder:
    metrics_stream = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "telemetry") \
        .load()

    # You would parse JSON etc. as in your streaming job.
    # For brevity, assume metrics_stream has:
    # timestamp, metric_name, value, source

    # Drift (streaming style: we can approximate with windowed ops or use batch‑like logic)
    drift_stream = page_hinkley_drift(metrics_stream, "cpu_usage")

    # For logs, you’d have a streaming logs source; here we assume a placeholder:
    logs_stream = metrics_stream.filter(col("metric_name") == "log_proxy")  # example

    # Correlation (structured streaming)
    correlation_stream = enterprise_event_correlation(
        logs_stream,
        metrics_stream,
        anomalies=metrics_stream,   # placeholder: you’d wire actual anomaly stream
        drift=drift_stream,
        window_minutes=1,
    )

    # Incident prediction
    incidents_stream = predict_incidents(
        correlation_stream,
        anomalies=metrics_stream,   # placeholder
        drift=drift_stream,
    )

    # Remediation graph
    remediation_stream = build_remediation_graph(incidents_stream)

    # Self‑healing: for streaming, we typically sink to a table/queue and have a controller consume.
    query = (
        remediation_stream.writeStream
        .outputMode("append")
        .format("console")
        .start()
    )

    query.awaitTermination()
