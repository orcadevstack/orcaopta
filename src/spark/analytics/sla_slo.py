from pyspark.sql import DataFrame
from pyspark.sql.functions import col, avg

def compute_slo(df: DataFrame, error_level: str = "ERROR"):
    total = df.count()
    errors = df.filter(col("level") == error_level).count()
    if total == 0:
        return {"total": 0, "errors": 0, "error_rate": 0.0}
    return {
        "total": total,
        "errors": errors,
        "error_rate": errors / total,
    }

def aggregate_latency(df: DataFrame, metric_name: str = "request_latency_ms"):
    m = df.filter(col("metric_name") == metric_name)
    if m.count() == 0:
        return {}
    stats = m.groupBy("source").agg(avg("value").alias("avg_latency")).collect()
    return {row["source"]: row["avg_latency"] for row in stats}
