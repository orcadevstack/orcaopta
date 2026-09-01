from pyspark.sql import DataFrame
from pyspark.sql.functions import col, mean, stddev, when
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import StandardScaler

from orcaopta.spark.anomaly.feature_engineering import build_features


# ---------------------------------------------------------
# 1. Simple z-score anomaly detection
# ---------------------------------------------------------
def zscore_anomaly(df: DataFrame, metric_name: str = "cpu_usage", threshold: float = 3.0):
    m = df.filter(col("metric_name") == metric_name)

    stats = m.agg(
        mean("value").alias("mu"),
        stddev("value").alias("sigma")
    ).first()

    mu, sigma = stats["mu"], stats["sigma"]

    if sigma is None or sigma == 0:
        return m.withColumn("anomaly", col("value") > mu * 2)

    return (
        m.withColumn("z", (col("value") - mu) / sigma)
         .withColumn("anomaly", (col("z").abs() > threshold))
    )


# ---------------------------------------------------------
# 2. Feature-based clustering anomalies (KMeans)
# ---------------------------------------------------------
def kmeans_anomaly(df: DataFrame, metric_name: str = "cpu_usage", k: int = 3):
    # Build features
    features_df = build_features(df, metric_name)

    # Standardize features
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features",
        withMean=True,
        withStd=True
    )
    scaled = scaler.fit(features_df).transform(features_df)

    # Train KMeans
    kmeans = KMeans(featuresCol="scaled_features", predictionCol="cluster", k=k)
    model = kmeans.fit(scaled)

    clustered = model.transform(scaled)

    # Compute cluster distances (approx anomaly score)
    centers = model.clusterCenters()

    def distance_to_center(row):
        c = centers[row["cluster"]]
        v = row["scaled_features"]
        return float(v.squared_distance(c))

    # Add distance column
    rdd = clustered.rdd.map(
        lambda r: (*r, distance_to_center(r))
    )

    cols = clustered.columns + ["distance"]
    clustered_with_dist = clustered.sparkSession.createDataFrame(rdd, cols)

    # Mark anomalies as points far from their cluster center
    # Here we use a simple percentile threshold
    dist_stats = clustered_with_dist.agg(
        mean("distance").alias("mean_dist"),
        stddev("distance").alias("std_dist")
    ).first()

    mean_dist, std_dist = dist_stats["mean_dist"], dist_stats["std_dist"]

    if std_dist is None or std_dist == 0:
        threshold = mean_dist * 2
    else:
        threshold = mean_dist + 3 * std_dist

    return clustered_with_dist.withColumn(
        "cluster_anomaly",
        when(col("distance") > threshold, True).otherwise(False)
    )


# ---------------------------------------------------------
# 3. Unified anomaly detection interface
# ---------------------------------------------------------
def detect_anomalies(df: DataFrame, metric_name: str = "cpu_usage"):
    """
    Runs both z-score and KMeans-based anomaly detection.
    Returns a DataFrame with anomaly flags.
    """
    z_df = zscore_anomaly(df, metric_name)
    k_df = kmeans_anomaly(df, metric_name)

    # Join on common keys
    joined = (
        z_df.alias("z")
        .join(
            k_df.alias("k"),
            on=["timestamp", "metric_name", "source", "value"],
            how="inner"
        )
        .select(
            "timestamp",
            "metric_name",
            "source",
            "value",
            "z.z",
            "z.anomaly",
            "k.cluster",
            "k.distance",
            "k.cluster_anomaly"
        )
    )

    return joined
