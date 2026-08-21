import pandas as pd

def validate(df: pd.DataFrame):
    assert "cpu_usage" in df.columns, "Missing cpu_usage column"
    assert "requests" in df.columns, "Missing requests column"

    assert df["cpu_usage"].between(0, 1).all(), "cpu_usage out of [0,1] range"
    assert (df["requests"] >= 0).all(), "requests must be non-negative"

    print("Data validation passed.")

if __name__ == "__main__":
    df = pd.read_csv("data/processed/train.csv")
    validate(df)
