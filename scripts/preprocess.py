import pandas as pd
from orcaopta.utils import ensure_dir

ensure_dir("data/processed")

df = pd.read_csv("data/raw/cloud_metrics_raw.csv")

# Example cleaning
df = df.dropna()
df["cpu_usage"] = df["cpu_usage"].clip(0, 1)

df.to_csv("data/processed/train.csv", index=False)

print("Processed dataset saved to data/processed/train.csv")
