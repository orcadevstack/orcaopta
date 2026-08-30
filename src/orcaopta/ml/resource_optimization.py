import joblib
import pandas as pd
from sklearn.tree import DecisionTreeRegressor

from src.orcaopta.ml.preprocess import clean, normalize, train_test_split
from src.orcaopta.ml.config import RESOURCE_MODEL

from orcaopta.utils.tracing import setup_tracing
tracer = setup_tracing()



def train_resource_optimizer(df: pd.DataFrame, target: str):
    """
    Train a DecisionTreeRegressor for resource optimization.
    Saves the trained model to RESOURCE_MODEL.
    """
    with tracer.start_as_current_span("resource-opt-train") as span:
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
        model = DecisionTreeRegressor()
        model.fit(train_X, train_y)

        # Save model
        joblib.dump(model, RESOURCE_MODEL)
        span.set_attribute("model_path", RESOURCE_MODEL)

        return model



def optimize_resources(model, df: pd.DataFrame):
    """
    Predict optimized resource allocations using a trained DecisionTreeRegressor.
    Returns: array of recommended resource values.
    """
    with tracer.start_as_current_span("resource-opt-predict") as span:
        span.set_attribute("rows", len(df))

        df_clean = clean(df)
        df_norm = normalize(df_clean)

        preds = model.predict(df_norm)
        return preds
