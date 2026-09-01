from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count

def detect_failure_patterns(logs: DataFrame):
    patterns = (
        logs.filter(col("level") == "ERROR")
            .groupBy("message")
            .agg(count("*").alias("occurrences"))
            .orderBy(col("occurrences").desc())
    )
    return patterns
