from pyspark.sql import DataFrame
from pyspark.sql.functions import col, avg, stddev, lag
from pyspark.sql.window import Window

def page_hinkley_drift(df: DataFrame, metric_name: str = "cpu_usage", delta: float = 0.005, lambda_: float = 50.0):
    """
    Simple Page-Hinkley-like drift detector.
    """

    w = Window.partitionBy("source", "metric_name").orderBy("timestamp")

    m = df.filter(col("metric_name") == metric_name).withColumn("value_float", col("value").cast("double"))

    m = m.withColumn("mean_value", avg("value_float").over(w))
    m = m.withColumn("diff", col("value_float") - col("mean_value"))

    m = m.withColumn("cum_diff", avg("diff").over(w))

    m = m.withColumn(
        "is_drift",
        (col("cum_diff") > lambda_ + delta)
    )

    return m


def simple_ks_drift(df: DataFrame, metric_name: str = "cpu_usage"):
    """
    Very rough KS-like drift: compare early vs late distribution.
    """

    m = df.filter(col("metric_name") == metric_name)

    total = m.count()
    if total < 20:
        return m.withColumn("is_drift", col("value") * 0 == 1)  # all False

    half = int(total / 2)

    early = m.orderBy("timestamp").limit(half)
    late = m.orderBy("timestamp").sort(col("timestamp").desc()).limit(half)

    early_stats = early.agg(avg("value").alias("mu_e"), stddev("value").alias("sigma_e")).first()
    late_stats = late.agg(avg("value").alias("mu_l"), stddev("value").alias("sigma_l")).first()

    mu_e, mu_l = early_stats["mu_e"], late_stats["mu_l"]

    diff = abs(mu_l - mu_e)

    threshold = (early_stats["sigma_e"] or 0) + (late_stats["sigma_l"] or 0)

    is_drift = diff > threshold

    return m.withColumn("is_drift", col("value") * 0 + int(is_drift))
