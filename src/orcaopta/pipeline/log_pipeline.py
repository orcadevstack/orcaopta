from typing import Dict, Any, List

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

from orcaopta.ml.training.continuous_learning import ContinuousLearningEngine


def build_spark_session(app_name: str = "orcaopta-log-pipeline") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .getOrCreate()
    )


def get_log_schema() -> StructType:
    return StructType([
        StructField("timestamp", StringType(), True),
        StructField("source", StringType(), True),
        StructField("latency_ms", DoubleType(), True),
        StructField("errors", DoubleType(), True),
        StructField("replication_lag_ms", DoubleType(), True),
        StructField("storage_usage_gb", DoubleType(), True),
        StructField("cpu_percent", DoubleType(), True),
        StructField("memory_percent", DoubleType(), True),
    ])


def run_log_pipeline(
    kafka_bootstrap: str,
    kafka_topic: str,
    config_state: Dict[str, Any],
) -> None:
    """
    Main entrypoint: read logs from Kafka with Spark, feed them into ContinuousLearningEngine.
    """
    spark = build_spark_session()
    schema = get_log_schema()
    engine = ContinuousLearningEngine()

    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap)
        .option("subscribe", kafka_topic)
        .load()
    )

    json_df = df.selectExpr("CAST(value AS STRING) as json_str")

    parsed_df = json_df.select(
        from_json(col("json_str"), schema).alias("data")
    ).select("data.*")

    def foreach_batch(batch_df, batch_id: int) -> None:
        rows = batch_df.collect()
        raw_logs: List[Dict[str, Any]] = [
            {
                "timestamp": r["timestamp"],
                "source": r["source"],
                "latency_ms": r["latency_ms"],
                "errors": r["errors"],
                "replication_lag_ms": r["replication_lag_ms"],
                "storage_usage_gb": r["storage_usage_gb"],
                "cpu_percent": r["cpu_percent"],
                "memory_percent": r["memory_percent"],
            }
            for r in rows
        ]

        engine.process_logs(raw_logs, config_state)

    (
        parsed_df.writeStream
        .foreachBatch(foreach_batch)
        .outputMode("update")
        .start()
        .awaitTermination()
    )
