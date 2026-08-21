import os
import shutil
from datetime import datetime
from src.utils import ensure_dir

VERSION_DIR = "data/versions"

def save_version(path: str):
    ensure_dir(VERSION_DIR)
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    base = os.path.basename(path)
    versioned = os.path.join(VERSION_DIR, f"{ts}-{base}")
    shutil.copy2(path, versioned)
    print(f"Saved dataset version: {versioned}")

if __name__ == "__main__":
    save_version("data/processed/train.csv")
