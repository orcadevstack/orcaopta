from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, lit, avg, stddev, count, expr
)


def compute_risk_score(correlation: DataFrame):
    """
    Compute a numeric risk score based on correlated logs + metrics.
    Higher log_count + metric_count = higher risk.
    """

    return correlation.withColumn(
        "risk_score",
        (
            (col("log_count") * 0.6) +
            (col("metric_count") * 0.4)
        )
    )


def classify_risk(df: DataFrame):
    """
    Convert numeric risk score into HIGH / MEDIUM / LOW categories.
    """

    return df.withColumn(
        "incident_level",
        when(col("risk_score") > 80, "CRITICAL")
        .when(col("risk_score") > 40, "HIGH")
        .when(col("risk_score") > 20, "MEDIUM")
        .otherwise("LOW")
    )


def add_anomaly_signal(df: DataFrame, anomalies: DataFrame):
    """
    Join anomaly flags into the correlation dataset.
    """

    return (
        df.join(
            anomalies.select(
                "timestamp",
                "metric_name",
                "source",
                "anomaly",
                "cluster_anomaly"
            ),
            on=["timestamp", "metric_name", "source"],
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


def add_drift_signal(df: DataFrame, drift: DataFrame):
    """
    Join drift detection results into the correlation dataset.
    """

    return (
        df.join(
            drift.select(
                "timestamp",
                "metric_name",
                "source",
                "is_drift"
            ),
            on=["timestamp", "metric_name", "source"],
            how="left"
        )
        .withColumn(
            "drift_signal",
            when(col("is_drift") == True, lit(1)).otherwise(lit(0))
        )
    )


def final_incident_score(df: DataFrame):
    """
    Combine all signals into a final incident prediction score.
    """

    return df.withColumn(
        "incident_score",
        (
            col("risk_score") +
            (col("anomaly_signal") * 25) +
            (col("cluster_anomaly_signal") * 20) +
            (col("drift_signal") * 30)
        )
    ).withColumn(
        "incident_prediction",
        when(col("incident_score") > 120, "IMMINENT FAILURE")
        .when(col("incident_score") > 80, "HIGH RISK")
        .when(col("incident_score") > 40, "MEDIUM RISK")
        .otherwise("LOW RISK")
    )


def predict_incidents(correlation: DataFrame, anomalies: DataFrame, drift: DataFrame):
    """
    Full incident prediction pipeline:
    - risk score
    - anomaly signals
    - drift signals
    - final incident score
    """

    # Step 1: risk score from correlation
    scored = compute_risk_score(correlation)

    # Step 2: join anomaly signals
    scored = add_anomaly_signal(scored, anomalies)

    # Step 3: join drift signals
    scored = add_drift_signal(scored, drift)

    # Step 4: classify risk + compute final score
    scored = classify_risk(scored)
    scored = final_incident_score(scored)

    return scored
