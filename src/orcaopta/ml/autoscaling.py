import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.orcaopta.ml.preprocess import clean, normalize, train_test_split
from src.orcaopta.ml.config import AUTOSCALE_MODEL

from orcaopta.utils.tracing import setup_tracing
tracer = setup_tracing()



def train_autoscaler(df: pd.DataFrame, target: str = "scale"):
    """
    Train a RandomForestClassifier autoscaling model.
    Saves the trained model to AUTOSCALE_MODEL.
    """
    with tracer.start_as_current_span("autoscale-train") as span:
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

        # Correct train/test split
        train_X, test_X = train_test_split(X)
        train_y, test_y = train_test_split(y)

        # Train model
        model = RandomForestClassifier()
        model.fit(train_X, train_y)

        # Save model
        joblib.dump(model, AUTOSCALE_MODEL)
        span.set_attribute("model_path", AUTOSCALE_MODEL)

        return model



def autoscale_decision(model, df: pd.DataFrame):
    """
    Predict autoscaling decisions using a trained RandomForestClassifier.
    Returns: array of decisions (e.g., scale_up, scale_down, hold)
    """
    with tracer.start_as_current_span("autoscale-predict") as span:
        span.set_attribute("rows", len(df))

        df_clean = clean(df)
        df_norm = normalize(df_clean)

        preds = model.predict(df_norm)
        return preds
