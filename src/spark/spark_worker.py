import os
import json
import logging

logger = logging.getLogger("spark.worker")

# ============================================================
# SAFE IMPORT OF PIPELINE ENGINE
# ============================================================

try:
    from spark.pipelines.pipeline_main import run_pipeline
    PIPELINE_AVAILABLE = True
except Exception as e:
    PIPELINE_AVAILABLE = False
    logger.warning(f"[SparkWorker] Spark pipeline subsystem unavailable: {e}")


# ============================================================
# ENTERPRISE SPARK WORKER
# ============================================================

class SparkWorker:
    """
    Enterprise-grade Spark worker for Orcaopta.

    Features:
    - Safe imports
    - Graceful fallback when Spark is missing
    - Pipeline execution
    - Job execution
    - SQL execution
    - Data ingestion
    - Config loading
    - Status reporting
    - Unified JSON responses
    """

    def __init__(self, config_path: str = "/app/spark_config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    # ============================================================
    # CONFIG LOADING
    # ============================================================

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            logger.warning(f"[SparkWorker] No Spark config found at {self.config_path}. Using defaults.")
            return {}

        try:
            with open(self.config_path) as f:
                cfg = json.load(f)
                logger.info("[SparkWorker] Spark config loaded successfully.")
                return cfg
        except Exception as e:
            logger.error(f"[SparkWorker] Failed to load Spark config: {e}")
            return {}

    # ============================================================
    # STATUS
    # ============================================================

    def status(self) -> dict:
        return {
            "spark_available": PIPELINE_AVAILABLE,
            "config_loaded": bool(self.config),
            "config_path": self.config_path,
        }

    # ============================================================
    # PIPELINE EXECUTION
    # ============================================================

    def run_pipeline(self, pipeline_name: str = None):
        if not PIPELINE_AVAILABLE:
            return {
                "status": "error",
                "message": "Spark pipeline subsystem unavailable.",
                "details": "PySpark or pipeline_main import failed."
            }

        try:
            cfg = self.config.get(pipeline_name, {}) if pipeline_name else self.config
            logger.info(f"[SparkWorker] Running Spark pipeline: {pipeline_name or 'default'}")

            result = run_pipeline(cfg)

            return {
                "status": "success",
                "pipeline": pipeline_name or "default",
                "slo": result.get("slo"),
                "anomalies": "DataFrame returned (not serialized)",
            }

        except Exception as e:
            logger.error(f"[SparkWorker] Pipeline execution failed: {e}")
            return {
                "status": "error",
                "message": "Pipeline execution failed",
                "details": str(e),
            }

    # ============================================================
    # JOB EXECUTION
    # ============================================================

    def run_job(self, job_name: str):
        """
        Enterprise job wrapper.
        """
        logger.info(f"[SparkWorker] Running Spark job: {job_name}")
        return self.run_pipeline(job_name)

    # ============================================================
    # SQL EXECUTION (OPTIONAL)
    # ============================================================

    def run_sql(self, query: str):
        if not PIPELINE_AVAILABLE:
            return {"status": "error", "message": "Spark unavailable"}

        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()

            logger.info(f"[SparkWorker] Running SQL query: {query}")
            df = spark.sql(query)

            return {
                "status": "success",
                "query": query,
                "rows": df.take(50),  # sample only
            }

        except Exception as e:
            logger.error(f"[SparkWorker] SQL execution failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # INGESTION
    # ============================================================

    def ingest(self, source: str):
        """
        Ingest data from a source (file, S3, logs, etc.)
        """
        if not PIPELINE_AVAILABLE:
            return {"status": "error", "message": "Spark unavailable"}

        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.getOrCreate()

            logger.info(f"[SparkWorker] Ingesting source: {source}")
            df = spark.read.format("json").load(source)

            return {
                "status": "success",
                "source": source,
                "rows": df.take(20),
            }

        except Exception as e:
            logger.error(f"[SparkWorker] Ingestion failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # HEARTBEAT
    # ============================================================

    def run(self):
        """
        Minimal heartbeat used by supervisor.
        """
        if PIPELINE_AVAILABLE:
            logger.info("[SparkWorker] Heartbeat OK — Spark subsystem detected.")
            return {"status": "ok", "spark": True}
        else:
            logger.warning("[SparkWorker] Heartbeat — Spark subsystem NOT available.")
            return {"status": "degraded", "spark": False}
