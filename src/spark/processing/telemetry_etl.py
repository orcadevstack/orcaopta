from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def normalize_metrics(df: DataFrame) -> DataFrame:
    # Example: keep only relevant columns
    keep = ["timestamp", "metric_name", "value", "source"]
    return df.select(*[c for c in keep if c in df.columns]).filter(col("value").isNotNull())
