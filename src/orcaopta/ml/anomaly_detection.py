import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from orcaopta.ml.preprocess import clean, normalize, train_test_split
from orcaopta.ml.config import ANOMALY_MODEL

from orcaopta.utils.tracing import setup_tracing
tracer = setup_tracing()


def train_anomaly(df: pd.DataFrame):
    """
    Train an IsolationForest anomaly detection model.
    Saves the trained model to ANOMALY_MODEL.
    """
    with tracer.start_as_current_span("anomaly-train") as span:
        span.set_attribute("rows", len(df))

        # Preprocess
        df_clean = clean(df)
        df_norm = normalize(df_clean)
        train, _ = train_test_split(df_norm)

        # Train model
        model = IsolationForest(contamination=0.05)
        model.fit(train)

        # Save model
        joblib.dump(model, ANOMALY_MODEL)
        span.set_attribute("model_path", ANOMALY_MODEL)

        return model



def predict_anomaly(model, df: pd.DataFrame):
    """
    Predict anomalies using a trained IsolationForest model.
    Returns: array of -1 (anomaly) or 1 (normal)
    """
    with tracer.start_as_current_span("anomaly-predict") as span:
        span.set_attribute("rows", len(df))

        df_clean = clean(df)
        df_norm = normalize(df_clean)

        preds = model.predict(df_norm)
        return preds
