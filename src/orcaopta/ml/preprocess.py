import pandas as pd
from sklearn.preprocessing import StandardScaler

from orcaopta.utils.tracing import setup_tracing
tracer = setup_tracing()


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with missing values.
    Returns a new cleaned DataFrame.
    """
    with tracer.start_as_current_span("preprocess-clean") as span:
        span.set_attribute("rows_before", len(df))

        df_clean = df.dropna().copy()

        span.set_attribute("rows_after", len(df_clean))
        return df_clean


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize numeric columns using StandardScaler.
    Returns a new normalized DataFrame.
    """
    with tracer.start_as_current_span("preprocess-normalize") as span:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        span.set_attribute("num_cols", len(num_cols))

        if not num_cols:
            # No numeric columns → return unchanged
            return df.copy()

        scaler = StandardScaler()
        df_norm = df.copy()
        df_norm[num_cols] = scaler.fit_transform(df_norm[num_cols])

        return df_norm



def train_test_split(df: pd.DataFrame, ratio: float = 0.8):
    """
    Split a DataFrame into train and test sets.
    Returns (train_df, test_df).
    """
    with tracer.start_as_current_span("preprocess-split") as span:
        span.set_attribute("rows", len(df))
        span.set_attribute("ratio", ratio)

        if len(df) == 0:
            return df, df

        split = int(len(df) * ratio)
        train = df.iloc[:split].copy()
        test = df.iloc[split:].copy()

        span.set_attribute("train_rows", len(train))
        span.set_attribute("test_rows", len(test))

        return train, test
