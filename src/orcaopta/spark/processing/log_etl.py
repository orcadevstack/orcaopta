from pyspark.sql import DataFrame
from pyspark.sql.functions import regexp_extract, col

def parse_basic_fields(df: DataFrame) -> DataFrame:
    # Example: extract level and message from log line
    level_pattern = r"\b(INFO|WARN|ERROR|DEBUG|CRITICAL)\b"
    return (
        df.withColumn("level", regexp_extract(col("value"), level_pattern, 1))
          .withColumn("message", col("value"))
    )

def filter_noise(df: DataFrame) -> DataFrame:
    return df.filter(~col("message").contains("healthcheck"))
