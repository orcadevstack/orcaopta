import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.orcaopta.ml.preprocess import clean, normalize, train_test_split
from src.orcaopta.ml.config import FORECAST_MODEL

from orcaopta.utils.tracing import setup_tracing
tracer = setup_tracing()



def train_forecast(df: pd.DataFrame, target: str):
    """
    Train a LinearRegression forecasting model.
    Saves the trained model to FORECAST_MODEL.
    """
    with tracer.start_as_current_span("forecast-train") as span:
        span.set_attribute("rows", len(df))
        span.set_attribute("target", target)

        # Validate target column
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found in dataframe")

        # Preprocess
        df_clean = clean(df)
        df_norm = normalize(df_clean)

        # Split features/target
        X = df_norm.drop(columns=[target])
        y = df_norm[target]

        # Train/test split (correct way)
        train_X, test_X = train_test_split(X)
        train_y, test_y = train_test_split(y)

        # Train model
        model = LinearRegression()
        model.fit(train_X, train_y)

        # Save model
        joblib.dump(model, FORECAST_MODEL)
        span.set_attribute("model_path", FORECAST_MODEL)

        return model



def predict_future(model, df: pd.DataFrame):
    """
    Predict future values using a trained LinearRegression model.
    Returns: array of predictions
    """
    with tracer.start_as_current_span("forecast-predict") as span:
        span.set_attribute("rows", len(df))

        df_clean = clean(df)
        df_norm = normalize(df_clean)

        preds = model.predict(df_norm)
        return preds
