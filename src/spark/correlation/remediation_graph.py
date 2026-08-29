from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, lit

def build_remediation_graph(incidents: DataFrame):
    """
    Build remediation actions based on incident_score, level, drift, anomalies.
    """

    df = incidents.withColumn(
        "action",
        when(col("incident_prediction") == "IMMINENT FAILURE", lit("IMMEDIATE_REMEDIATION"))
        .when(col("incident_prediction") == "HIGH RISK", lit("AGGRESSIVE_REMEDIATION"))
        .when(col("incident_prediction") == "MEDIUM RISK", lit("MONITOR_AND_PREPARE"))
        .otherwise(lit("NO_ACTION"))
    ).withColumn(
        "remediation_type",
        when(col("drift_signal") == 1, lit("CONFIG_DRIFT_FIX"))
        .when(col("anomaly_signal") == 1, lit("RESOURCE_TUNING"))
        .when(col("cluster_anomaly_signal") == 1, lit("CLUSTER_REBALANCE"))
        .otherwise(lit("NONE"))
    ).withColumn(
        "remediation_target",
        col("source")
    )

    return df.select(
        "timestamp",
        "source",
        "metric_name",
        "incident_prediction",
        "incident_score",
        "action",
        "remediation_type",
        "remediation_target"
    )
