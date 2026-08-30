import subprocess
import yaml
import os

BASE = "/app/src/orcaopta/projects"

def load_manifest():
    with open(f"{BASE}/manifest.yaml") as f:
        return yaml.safe_load(f)

def run_project(job: str):
    manifest = load_manifest()
    print(f"[ORCA PROJECT] Running job: {job}")

    if job == "train_rl":
        subprocess.run(["python", "/app/src/orcaopta/train/train_rl.py"])
    elif job == "autoscale":
        subprocess.run(["python", "/app/src/orcaopta/train/autoscale.py"])
    else:
        raise ValueError(f"Unknown job: {job}")
