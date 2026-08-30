import logging

# Correct import path for your SparkWorker
from spark.spark_worker import SparkWorker

logger = logging.getLogger("orcaopta.mcp.tools.spark")

# Create a single shared worker instance
worker = SparkWorker()


# ============================================================
# Run a Spark Job
# ============================================================

def tool_spark_run_job(job_name: str):
    """
    Run a Spark job by name.
    Example: daily_metrics, cluster_aggregation
    """
    try:
        logger.info(f"[SparkTool] Running Spark job: {job_name}")
        result = worker.run(job_name)
        return {
            "status": "ok",
            "job": job_name,
            "result": result,
        }
    except Exception as e:
        logger.error(f"[SparkTool] Job failed: {job_name} - {e}")
        return {
            "status": "error",
            "job": job_name,
            "error": str(e),
        }


# ============================================================
# Run a Spark Pipeline
# ============================================================

def tool_spark_pipeline(pipeline_name: str):
    """
    Run a Spark pipeline by name.
    Example: cloud_ingestion, analytics_pipeline
    """
    try:
        logger.info(f"[SparkTool] Running Spark pipeline: {pipeline_name}")
        result = worker.run_pipeline(pipeline_name)
        return {
            "status": "ok",
            "pipeline": pipeline_name,
            "result": result,
        }
    except Exception as e:
        logger.error(f"[SparkTool] Pipeline failed: {pipeline_name} - {e}")
        return {
            "status": "error",
            "pipeline": pipeline_name,
            "error": str(e),
        }


# ============================================================
# Spark Ingestion
# ============================================================

def tool_spark_ingest(source: str):
    """
    Ingest data from a source into Spark.
    Example: s3://bucket/logs, /var/log/syslog
    """
    try:
        logger.info(f"[SparkTool] Ingesting source: {source}")
        result = worker.ingest(source)
        return {
            "status": "ok",
            "source": source,
            "result": result,
        }
    except Exception as e:
        logger.error(f"[SparkTool] Ingestion failed: {source} - {e}")
        return {
            "status": "error",
            "source": source,
            "error": str(e),
        }
