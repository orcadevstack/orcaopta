from pyspark.sql import DataFrame
from pyspark.sql.functions import col, window, count

def error_heatmap(df: DataFrame, window_minutes: int = 5):
    return (
        df.groupBy(
            window(col("timestamp"), f"{window_minutes} minutes"),
            col("source"),
            col("level"),
        )
        .agg(count("*").alias("count"))
    )
