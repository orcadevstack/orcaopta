import pandas as pd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    # Example features
    df["cpu_rolling_mean"] = df["cpu_usage"].rolling(window=5, min_periods=1).mean()
    df["cpu_rolling_std"] = df["cpu_usage"].rolling(window=5, min_periods=1).std()
    df["requests_per_cpu"] = df["requests"] / (df["cpu_usage"] + 1e-6)
    return df

if __name__ == "__main__":
    df = pd.read_csv("data/processed/train.csv")
    df = add_features(df)
    df.to_csv("data/processed/train_features.csv", index=False)
    print("Saved feature-engineered dataset to data/processed/train_features.csv")
