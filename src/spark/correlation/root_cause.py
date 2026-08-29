from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, lit, avg, stddev, count, expr
)


def compute_base_score(correlation: DataFrame):
    """
    Base RCA score from correlation signals.
    """
    return correlation.withColumn(
        "base_score",
        (
            (col("log_count") * 0.5) +
            (col("metric_count") * 0.4)
        )
    )


def add_anomaly_weight(df: DataFrame):
    """
    Add anomaly influence to RCA score.
    """
    return df.withColumn(
        "anomaly_weight",
        when(col("anomaly_signal") == 1, lit(25)).otherwise(lit(0))
    ).withColumn(
        "cluster_anomaly_weight",
        when(col("cluster_anomaly_signal") == 1, lit(20)).otherwise(lit(0))
    )


def add_drift_weight(df: DataFrame):
    """
    Add drift influence to RCA score.
    Drift is one of the strongest RCA signals.
    """
    return df.withColumn(
        "drift_weight",
        when(col("drift_signal") == 1, lit(35)).otherwise(lit(0))
    )


def add_latency_weight(df: DataFrame):
    """
    Latency spikes often indicate upstream root causes.
    """
    return df.withColumn(
        "latency_weight",
        when(col("avg_latency") > 200, lit(15))
        .when(col("avg_latency") > 100, lit(10))
        .otherwise(lit(0))
    )


def add_failure_pattern_weight(df: DataFrame, failure_patterns: DataFrame):
    """
    Join failure pattern occurrences into RCA scoring.
    """
    fp = failure_patterns.select(
        col("message").alias("fp_message"),
        col("occurrences").alias("fp_occurrences")
    )

    return (
        df.join(fp, df["metric_name"] == fp["fp_message"], "left")
          .withColumn(
              "failure_pattern_weight",
              when(col("fp_occurrences") > 20, lit(30))
              .when(col("fp_occurrences") > 10, lit(15))
              .otherwise(lit(0))
          )
    )


def compute_final_rca_score(df: DataFrame):
    """
    Combine all weights into final RCA score.
    """
    return df.withColumn(
        "root_cause_score",
        (
            col("base_score") +
            col("anomaly_weight") +
            col("cluster_anomaly_weight") +
            col("drift_weight") +
            col("latency_weight") +
            col("failure_pattern_weight")
        )
    )


def classify_root_cause(df: DataFrame):
    """
    Classify RCA severity.
    """
    return df.withColumn(
        "root_cause_level",
        when(col("root_cause_score") > 120, "PRIMARY_CAUSE")
        .when(col("root_cause_score") > 80, "LIKELY_CAUSE")
        .when(col("root_cause_score") > 40, "POSSIBLE_CAUSE")
        .otherwise("LOW_IMPACT")
    )


def root_cause(correlation: DataFrame, failure_patterns: DataFrame):
    """
    Full enterprise RCA pipeline.
    """

    # Step 1: base score
    df = compute_base_score(correlation)

    # Step 2: anomaly weights
    df = add_anomaly_weight(df)

    # Step 3: drift weights
    df = add_drift_weight(df)

    # Step 4: latency weights
    df = add_latency_weight(df)

    # Step 5: failure pattern weights
    df = add_failure_pattern_weight(df, failure_patterns)

    # Step 6: final RCA score
    df = compute_final_rca_score(df)

    # Step 7: classification
    df = classify_root_cause(df)

    # Step 8: sort by strongest root cause
    return df.orderBy(col("root_cause_score").desc())
