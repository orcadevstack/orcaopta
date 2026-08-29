from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

def create_spark(app_name: str = "OrcaoptaLogIngest") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .getOrCreate()
    )

def ingest_logs(spark: SparkSession, sources: dict):
    """
    sources = {
        "openstack": "s3a://logs/openstack/",
        "kubernetes": "s3a://logs/kubernetes/",
        ...
    }
    """
    frames = {}
    for name, path in sources.items():
        df = spark.read.text(path).withColumn("source", lit(name))
        frames[name] = df
    return frames

def union_all(frames: dict):
    it = iter(frames.values())
    base = next(it)
    for df in it:
        base = base.unionByName(df, allowMissingColumns=True)
    return base
