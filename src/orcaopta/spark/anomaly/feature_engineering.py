from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, avg, stddev, lag, when, abs, 
    window, count, max as spark_max, min as spark_min
)
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler


# ---------------------------------------------------------
# 1. Basic normalization
# ---------------------------------------------------------
def normalize(df: DataFrame, column: str = "value"):
    stats = df.agg(
        avg(column).alias("mean"),
        stddev(column).alias("std")
    ).first()

    mean, std = stats["mean"], stats["std"]

    if std is None or std == 0:
        return df.withColumn("normalized", col(column))

    return df.withColumn("normalized", (col(column) - mean) / std)


# ---------------------------------------------------------
# 2. Rolling window features
# ---------------------------------------------------------
def rolling_features(df: DataFrame, metric_name: str, window_size: int = 5):
    w = Window.partitionBy("source", "metric_name").orderBy("timestamp").rowsBetween(-window_size, 0)

    return (
        df.filter(col("metric_name") == metric_name)
          .withColumn("rolling_avg", avg("value").over(w))
          .withColumn("rolling_std", stddev("value").over(w))
    )


# ---------------------------------------------------------
# 3. Lag features (previous values)
# ---------------------------------------------------------
def lag_features(df: DataFrame, metric_name: str, lags=[1, 2, 3]):
    w = Window.partitionBy("source", "metric_name").orderBy("timestamp")

    out = df.filter(col("metric_name") == metric_name)
    for l in lags:
        out = out.withColumn(f"lag_{l}", lag("value", l).over(w))

    return out


# ---------------------------------------------------------
# 4. Rate of change (derivative)
# ---------------------------------------------------------
def rate_of_change(df: DataFrame):
    w = Window.partitionBy("source", "metric_name").orderBy("timestamp")
    return df.withColumn("prev_value", lag("value").over(w)) \
             .withColumn("rate_of_change", col("value") - col("prev_value"))


# ---------------------------------------------------------
# 5. Cluster-wide aggregations
# ---------------------------------------------------------
def cluster_aggregates(df: DataFrame):
    agg = (
        df.groupBy("metric_name")
          .agg(
              avg("value").alias("cluster_avg"),
              spark_max("value").alias("cluster_max"),
              spark_min("value").alias("cluster_min"),
              stddev("value").alias("cluster_std")
          )
    )
    return agg


# ---------------------------------------------------------
# 6. Assemble ML feature vector
# ---------------------------------------------------------
def assemble_features(df: DataFrame, feature_cols=None):
    if feature_cols is None:
        feature_cols = [
            "value",
            "normalized",
            "rolling_avg",
            "rolling_std",
            "rate_of_change"
        ]

    assembler = VectorAssembler(
        inputCols=[c for c in feature_cols if c in df.columns],
        outputCol="features"
    )

    return assembler.transform(df)


# ---------------------------------------------------------
# 7. Full feature engineering pipeline
# ---------------------------------------------------------
def build_features(df: DataFrame, metric_name: str):
    # Step 1: Normalize
    df = normalize(df)

    # Step 2: Rolling window features
    df = rolling_features(df, metric_name)

    # Step 3: Lag features
    df = lag_features(df, metric_name)

    # Step 4: Rate of change
    df = rate_of_change(df)

    # Step 5: Assemble ML features
    df = assemble_features(df)

    return df
