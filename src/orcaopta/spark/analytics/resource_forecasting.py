from pyspark.sql import DataFrame
from pyspark.sql.functions import col, window, avg
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession


def prepare_time_series(df: DataFrame, metric_name: str):
    """
    Convert telemetry metrics into a time-series dataset suitable for MLlib.
    """
    ts = (
        df.filter(col("metric_name") == metric_name)
          .select("timestamp", "value")
          .orderBy("timestamp")
    )

    # Convert timestamp to numeric (seconds)
    ts = ts.withColumn("ts_numeric", col("timestamp").cast("long"))

    return ts


def train_forecast_model(ts: DataFrame):
    """
    Train a simple linear regression model to forecast resource usage.
    """

    assembler = VectorAssembler(
        inputCols=["ts_numeric"],
        outputCol="features"
    )

    data = assembler.transform(ts).select("features", "value")

    lr = LinearRegression(featuresCol="features", labelCol="value")
    model = lr.fit(data)

    return model


def forecast_future(model, last_timestamp_numeric: int, steps: int = 5):
    """
    Forecast future resource usage for N future time steps.
    """

    spark = SparkSession.builder.getOrCreate()

    future_rows = [
        (last_timestamp_numeric + i * 60,)  # predict each minute
        for i in range(1, steps + 1)
    ]

    future_df = spark.createDataFrame(future_rows, ["ts_numeric"])

    assembler = VectorAssembler(
        inputCols=["ts_numeric"],
        outputCol="features"
    )

    future_df = assembler.transform(future_df)

    predictions = model.transform(future_df).select("ts_numeric", "prediction")

    return predictions


def forecast_resource_usage(df: DataFrame, metric_name: str = "cpu_usage"):
    """
    Full forecasting pipeline:
    - Prepare time-series
    - Train model
    - Predict future values
    """

    ts = prepare_time_series(df, metric_name)

    if ts.count() < 5:
        print(f"Not enough data to forecast {metric_name}")
        return None

    model = train_forecast_model(ts)

    last_ts = ts.orderBy(col("timestamp").desc()).first()["timestamp"].timestamp()

    predictions = forecast_future(model, int(last_ts))

    print(f"=== Forecast for {metric_name} ===")
    predictions.show(truncate=False)

    return predictions
