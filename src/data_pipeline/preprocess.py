import pandas as pd
from orcaopta.utils import ensure_dir

RAW_PATH = "data/raw/cloud_metrics_raw.csv"
PROCESSED_PATH = "data/processed/train.csv"

def preprocess():
    df = pd.read_csv(RAW_PATH)

    # Basic cleaning
    df = df.dropna()
    df = df[df["cpu_usage"] >= 0]
    df["cpu_usage"] = df["cpu_usage"].clip(0, 1)

    ensure_dir("data/processed")
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"Saved processed data to {PROCESSED_PATH}")

if __name__ == "__main__":
    preprocess()
