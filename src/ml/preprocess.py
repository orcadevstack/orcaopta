import pandas as pd
from sklearn.preprocessing import StandardScaler

def clean(df):
    return df.dropna()

def normalize(df):
    num_cols = df.select_dtypes(include="number").columns
    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])
    return df

def train_test_split(df, ratio=0.8):
    split = int(len(df) * ratio)
    return df.iloc[:split], df.iloc[split:]
