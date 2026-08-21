import pandas as pd

def load_csv(path):
    return pd.read_csv(path)

def load_github_raw(url):
    return pd.read_csv(url)
