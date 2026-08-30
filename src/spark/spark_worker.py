import os
import json
import logging


try:
    from spark.pipelines.pipeline_main import run_pipeline
    PIPELINE_AVAILABLE = True
except Exception as e:
    PIPELINE_AVAILABLE = False
    logging.getLogger("spark.worker").warning(
        f"Spark pipeline subsystem unavailable: {e}"
    )

logger = logging.getLogger("spark.worker")

class SparkWorker:
    def __init__(self):
        pass

    def run(self, job_name=None):
        print(f"SparkWorker running job: {job_name}")

class SparkWorker:
    """
    Enterprise-grade Spark worker for Orcaopta.
    - Safe imports
    - Graceful fallback when Spark is missing
    - Pipeline execution
    - Config loading
    - Status reporting
    """

    def __init__(self, config_path: str = "/app/spark_config.json"):
        self.config_path = config_path
        self.config = self._load_config()


    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            logger.warning(f"No Spark config found at {self.config_path}. Using defaults.")
            return {}

        try:
            with open(self.config_path) as f:
                cfg = json.load(f)
                logger.info("Spark config loaded successfully.")
                return cfg
        except Exception as e:
            logger.error(f"Failed to load Spark config: {e}")
            return {}

    def status(self) -> dict:
        return {
            "spark_available": PIPELINE_AVAILABLE,
            "config_loaded": bool(self.config),
            "config_path": self.config_path,
        }
    
    def run_pipeline(self, pipeline_name: str = None):
        """
        Run a Spark pipeline by name.
        If no name is provided, run the default pipeline.
        """

        if not PIPELINE_AVAILABLE:
            return {
                "status": "error",
                "message": "Spark pipeline subsystem unavailable.",
                "details": "PySpark or pipeline_main import failed."
            }

        try:
            cfg = self.config if pipeline_name is None else self.config.get(pipeline_name, {})
            logger.info(f"Running Spark pipeline: {pipeline_name or 'default'}")
            result = run_pipeline(cfg)

            return {
                "status": "success",
                "pipeline": pipeline_name or "default",
                "slo": result.get("slo"),
                "anomalies": "DataFrame returned (not serialized)",
            }

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return {
                "status": "error",
                "message": "Pipeline execution failed",
                "details": str(e),
            }

    def run_job(self, job_name: str):
        """
        Alias for run_pipeline, but named for enterprise job semantics.
        """
        return self.run_pipeline(job_name)

    def run(self):
        """
        Minimal heartbeat used by supervisor.
        """
        if PIPELINE_AVAILABLE:
            logger.info("SparkWorker heartbeat OK — Spark subsystem detected.")
            return {"status": "ok", "spark": True}
        else:
            logger.warning("SparkWorker heartbeat — Spark subsystem NOT available.")
            return {"status": "degraded", "spark": False}
