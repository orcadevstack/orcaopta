from pyspark.sql import DataFrame
from pyspark.sql.functions import col, avg, stddev

def cluster_behavior(metrics: DataFrame):
    stats = (
        metrics.groupBy("source", "metric_name")
               .agg(
                   avg("value").alias("avg_value"),
                   stddev("value").alias("std_value")
               )
    )
    return stats
