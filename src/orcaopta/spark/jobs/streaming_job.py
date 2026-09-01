from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, avg, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

def create_streaming_session():
    return (
        SparkSession.builder
        .appName("OrcaoptaStreamingDrift")
        .getOrCreate()
    )

def run_stream():
    spark = create_streaming_session()

    schema = StructType([
        StructField("timestamp", TimestampType()),
        StructField("metric_name", StringType()),
        StructField("value", DoubleType()),
        StructField("source", StringType()),
        StructField("baseline", DoubleType()),  # expected value
    ])

    raw = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "telemetry")
        .load()
    )

    parsed = raw.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    # windowed averages vs baseline → drift
    windowed = (
        parsed
        .withWatermark("timestamp", "5 minutes")
        .groupBy(
            window(col("timestamp"), "1 minute"),
            col("metric_name"),
            col("source"),
            col("baseline"),
        )
        .agg(avg("value").alias("avg_value"))
    )

    drift = windowed.withColumn(
        "drift",
        col("avg_value") - col("baseline")
    ).withColumn(
        "is_drift",
        (col("drift").abs() > 10)  # threshold, tune later
    )

    query = (
        drift.filter(col("is_drift") == True)
        .writeStream
        .outputMode("append")
        .format("console")
        .option("truncate", "false")
        .start()
    )

    query.awaitTermination()

if __name__ == "__main__":
    run_stream()
