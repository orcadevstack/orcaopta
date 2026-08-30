import os
import joblib
import logging
from pathlib import Path

from src.orcaopta.ml.config import (
    MODEL_DIR,
    CORE_MODEL_PATH,
    ANOMALY_MODELS,
    FORECAST_MODELS,
    RESOURCE_MODELS,
    AUTOSCALE_MODELS,
)

logger = logging.getLogger("orcaopta.model-utils")



def load_fallback_model():
    """
    Fallback model used when no versioned model is found.
    Prevents API crashes and keeps Orcaopta running.
    """
    from sklearn.linear_model import LinearRegression
    logger.warning("Using fallback LinearRegression model.")
    return LinearRegression()


def load_versioned_model(model_family: dict, version: str | None = None):
    """
    Load a versioned model from a model family.

    Example:
        load_versioned_model(ANOMALY_MODELS, "v2")

    If version is None:
        - load the highest available version
        - or fallback if none exist
    """

    # Explicit version requested
    if version:
        if version not in model_family:
            logger.error(f"Requested version '{version}' not found in model family.")
            return load_fallback_model()

        path = model_family[version]
        logger.info(f"Loading model version '{version}' from: {path}")

        if not Path(path).exists():
            logger.error(f"Model file missing: {path}")
            return load_fallback_model()

        return joblib.load(path)

    # No version specified → load latest
    if not model_family:
        logger.error("Model family is empty. No versions available.")
        return load_fallback_model()

    # Sort versions numerically: v1 < v2 < v3
    sorted_versions = sorted(model_family.keys(), key=lambda v: int(v.replace("v", "")))
    latest_version = sorted_versions[-1]
    latest_path = model_family[latest_version]

    logger.info(f"Loading latest model version '{latest_version}' from: {latest_path}")

    if not Path(latest_path).exists():
        logger.error(f"Latest model file missing: {latest_path}")
        return load_fallback_model()

    return joblib.load(latest_path)


def load_core_model():
    """
    Load the core Orcaopta model (non-versioned).
    """
    path = CORE_MODEL_PATH
    logger.info(f"Loading Orcaopta core model from: {path}")

    if not Path(path).exists():
        logger.error(f"Core model not found at: {path}")
        return load_fallback_model()

    model = joblib.load(path)
    logger.info("Core model loaded successfully.")
    return model


def load_anomaly(version: str | None = None):
    return load_versioned_model(ANOMALY_MODELS, version)

def load_forecast(version: str | None = None):
    return load_versioned_model(FORECAST_MODELS, version)

def load_resource_opt(version: str | None = None):
    return load_versioned_model(RESOURCE_MODELS, version)

def load_autoscale(version: str | None = None):
    return load_versioned_model(AUTOSCALE_MODELS, version)



def deploy_versioned_model(model_file: bytes, family: str, version: str):
    """
    Deploy a new versioned model.

    Example:
        deploy_versioned_model(file_bytes, "anomaly", "v3")
    """
    filename = f"{family}_{version}.pkl"
    path = MODEL_DIR / filename

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write model file
    with open(path, "wb") as f:
        f.write(model_file)

    logger.info(f"Model deployed: {path}")
    return path
