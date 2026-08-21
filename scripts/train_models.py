from src.ml import (
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling
)
import pandas as pd

df = pd.read_csv("data/processed/train.csv")

anomaly_detection.train_anomaly(df)
forecasting.train_forecast(df, target="cpu_usage")
resource_optimization.train_resource_optimizer(df, target="optimal_resources")
autoscaling.train_autoscaler(df, target="scale")

print("All models trained and saved.")
