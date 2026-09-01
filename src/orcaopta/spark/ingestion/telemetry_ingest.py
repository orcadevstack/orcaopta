from pyspark.sql import SparkSession

def ingest_metrics(spark: SparkSession, path: str):
    """
    Example: Prometheus/telemetry exported as Parquet/JSON.
    """
    return spark.read.parquet(path)
