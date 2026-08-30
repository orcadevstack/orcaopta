import logging
import json
import os
import logging.config


def get_logger(name: str = "orcaopta"):
    config_path = os.path.join("configs", "logging.json")

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            logging.config.dictConfig(config)

    logger = logging.getLogger(name)
    return logger

logger = get_logger()
logger.info("Model loaded")
