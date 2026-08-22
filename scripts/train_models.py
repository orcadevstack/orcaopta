import mlflow
import mlflow.sklearn
import pandas as pd

from src.utils.tracing import setup_tracing

from src.ml.data_loader import load_raw_data
from src.ml.preprocess import preprocess_data

from src.ml.anomaly_detection import train_anomaly_model
from src.ml.forecasting import train_forecasting_model
from src.ml.autoscaling import train_autoscaling_model
from src.ml.resource_optimization import train_resource_optimizer


def main():
  
    tracer = setup_tracing()

    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("orcaopta-ml")

    with tracer.start_as_current_span("orcaopta-ml-training") as span:
        span.set_attribute("stage", "start")

    
        with tracer.start_as_current_span("load-data") as s:
            df = load_raw_data()
            s.set_attribute("rows", len(df))
            s.set_attribute("columns", str(list(df.columns)))

        with tracer.start_as_current_span("preprocess-data") as s:
            df = preprocess_data(df)
            s.set_attribute("rows_after_preprocess", len(df))

        with tracer.start_as_current_span("train-anomaly") as s:
            anomaly_model = train_anomaly_model(df)
            mlflow.sklearn.log_model(anomaly_model, "anomaly_model")
            s.set_attribute("model", "anomaly_detection")

      
        with tracer.start_as_current_span("train-forecasting") as s:
            forecast_model = train_forecasting_model(df, target="cpu_usage")
            mlflow.sklearn.log_model(forecast_model, "forecast_model")
            s.set_attribute("model", "forecasting")

      
        with tracer.start_as_current_span("train-autoscaling") as s:
            autoscale_model = train_autoscaling_model(df, target="scale")
            mlflow.sklearn.log_model(autoscale_model, "autoscaling_model")
            s.set_attribute("model", "autoscaling")

     
        with tracer.start_as_current_span("train-resource-optimizer") as s:
            resource_model = train_resource_optimizer(df, target="optimal_resources")
            mlflow.sklearn.log_model(resource_model, "resource_optimizer_model")
            s.set_attribute("model", "resource_optimization")

        span.set_attribute("stage", "complete")


if __name__ == "__main__":
    main()
