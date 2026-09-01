from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, window, count, avg, stddev, when, lit
)


def correlate_counts(logs: DataFrame, metrics: DataFrame, window_minutes: int = 5):
    """
    Basic count correlation: logs + metrics in the same time window.
    """
    w = f"{window_minutes} minutes"

    logs_w = (
        logs.groupBy(window(col("timestamp"), w), col("source"))
            .agg(count("*").alias("log_count"))
    )

    metrics_w = (
        metrics.groupBy(window(col("timestamp"), w), col("source"))
               .agg(count("*").alias("metric_count"))
    )

    return logs_w.join(metrics_w, ["window", "source"], "outer")


def correlate_latency(metrics: DataFrame, window_minutes: int = 5):
    """
    Correlate latency spikes with metric anomalies.
    """
    w = f"{window_minutes} minutes"

    return (
        metrics.filter(col("metric_name") == "request_latency_ms")
               .groupBy(window(col("timestamp"), w), col("source"))
               .agg(
                   avg("value").alias("avg_latency"),
                   stddev("value").alias("std_latency")
               )
    )


def correlate_anomalies(correlation: DataFrame, anomalies: DataFrame):
    """
    Join anomaly signals into correlation dataset.
    """
    return (
        correlation.join(
            anomalies.select(
                "timestamp",
                "metric_name",
                "source",
                "anomaly",
                "cluster_anomaly"
            ),
            on=["source"],
            how="left"
        )
        .withColumn(
            "anomaly_signal",
            when(col("anomaly") == True, lit(1)).otherwise(lit(0))
        )
        .withColumn(
            "cluster_anomaly_signal",
            when(col("cluster_anomaly") == True, lit(1)).otherwise(lit(0))
        )
    )


def correlate_drift(correlation: DataFrame, drift: DataFrame):
    """
    Join drift detection signals.
    """
    return (
        correlation.join(
            drift.select("source", "metric_name", "is_drift"),
            on=["source"],
            how="left"
        )
        .withColumn(
            "drift_signal",
            when(col("is_drift") == True, lit(1)).otherwise(lit(0))
        )
    )


def weighted_correlation(df: DataFrame):
    """
    Compute weighted correlation score combining:
    - log_count
    - metric_count
    - anomaly signals
    - drift signals
    - latency spikes
    """

    return df.withColumn(
        "correlation_score",
        (
            (col("log_count") * 0.4) +
            (col("metric_count") * 0.3) +
            (col("anomaly_signal") * 20) +
            (col("cluster_anomaly_signal") * 15) +
            (col("drift_signal") * 25) +
            (col("avg_latency") * 0.01)
        )
    )


def enterprise_event_correlation(
    logs: DataFrame,
    metrics: DataFrame,
    anomalies: DataFrame,
    drift: DataFrame,
    window_minutes: int = 5
):
    """
    Full enterprise correlation pipeline.
    """

    # Step 1: basic counts
    base = correlate_counts(logs, metrics, window_minutes)

    # Step 2: latency correlation
    latency = correlate_latency(metrics, window_minutes)

    # Step 3: join latency
    corr = base.join(latency, ["window", "source"], "left")

    # Step 4: join anomalies
    corr = correlate_anomalies(corr, anomalies)

    # Step 5: join drift
    corr = correlate_drift(corr, drift)

    # Step 6: weighted correlation score
    corr = weighted_correlation(corr)

    return corr
