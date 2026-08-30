from pathlib import Path
import os

LOCAL_MODEL_DIR = Path("models")
LOCAL_DATA_DIR = Path("data/processed")

DEFAULT_MODEL_DIR = Path("/app/models")
DEFAULT_DATA_DIR = Path("/app/data/processed")

MODEL_DIR = Path(os.getenv("ORCAOPTA_MODEL_DIR", DEFAULT_MODEL_DIR))
DATA_DIR = Path(os.getenv("ORCAOPTA_DATA_DIR", DEFAULT_DATA_DIR))

# Ensure directories exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)



CORE_MODEL_NAME = os.getenv("ORCAOPTA_MODEL_NAME", "orcaopta_core_model.pkl")
CORE_MODEL_PATH = MODEL_DIR / CORE_MODEL_NAME



ANOMALY_MODEL = MODEL_DIR / "anomaly_model.pkl"
FORECAST_MODEL = MODEL_DIR / "forecast_model.pkl"
RESOURCE_MODEL = MODEL_DIR / "resource_opt_model.pkl"
AUTOSCALE_MODEL = MODEL_DIR / "autoscale_model.pkl"


ANOMALY_MODELS = {
    "v1": MODEL_DIR / "anomaly_v1.pkl",
    "v2": MODEL_DIR / "anomaly_v2.pkl",
    "v3": MODEL_DIR / "anomaly_v3.pkl",
}

FORECAST_MODELS = {
    "v1": MODEL_DIR / "forecast_v1.pkl",
    "v2": MODEL_DIR / "forecast_v2.pkl",
    "v3": MODEL_DIR / "forecast_v3.pkl",
}

RESOURCE_MODELS = {
    "v1": MODEL_DIR / "resource_opt_v1.pkl",
    "v2": MODEL_DIR / "resource_opt_v2.pkl",
    "v3": MODEL_DIR / "resource_opt_v3.pkl",
}

AUTOSCALE_MODELS = {
    "v1": MODEL_DIR / "autoscale_v1.pkl",
    "v2": MODEL_DIR / "autoscale_v2.pkl",
    "v3": MODEL_DIR / "autoscale_v3.pkl",
}


DATABASE_URL = os.getenv("ORCAOPTA_DB_URL", "sqlite:///orcaopta.db")

if DATABASE_URL.startswith("sqlite"):
    DATABASE_BACKEND = "SQLite"
elif DATABASE_URL.startswith("postgres"):
    DATABASE_BACKEND = "PostgreSQL"
elif DATABASE_URL.startswith("mysql"):
    DATABASE_BACKEND = "MySQL"
else:
    DATABASE_BACKEND = "Unknown"


CLOUD_STORAGE_ENDPOINT = os.getenv("ORCAOPTA_CLOUD_ENDPOINT")
CLOUD_STORAGE_BUCKET = os.getenv("ORCAOPTA_CLOUD_BUCKET", "orcaopta-data")

# Encrypted credentials (decrypted in data_loader)
CLOUD_ACCESS_KEY = os.getenv("ORCAOPTA_CLOUD_ACCESS_KEY")
CLOUD_SECRET_KEY = os.getenv("ORCAOPTA_CLOUD_SECRET_KEY")


QUEUE_BACKEND = os.getenv("ORCAOPTA_QUEUE_BACKEND", "local")
