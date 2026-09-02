from pyspark.sql import SparkSession
from orcaopta.cloud.cloudoperator.api import CloudBackend
from orcaopta.core.config_loader import load_config


class SparkAPI(CloudBackend):
    """
    Spark backend for Orcaopta Cloud Brain.
    Provides distributed log processing, feature extraction,
    and ML/RL data preparation.
    """

    def __init__(self):
        cfg = load_config().spark
        self.enabled = cfg.enabled

        if not self.enabled:
            self.spark = None
            return

        # Build Spark session
        self.spark = (
            SparkSession.builder
            .appName(cfg.app_name or "OrcaoptaSpark")
            .master(cfg.master or "spark://spark-master:7077")
            .getOrCreate()
        )

        self.input_path = cfg.input_path or "/app/data/raw_logs"
        self.output_path = cfg.output_path or "/app/data/spark_processed"

    def backend_name(self):
        return "spark"

    # ---------------------------------------------------------
    # CloudBackend interface methods
    # ---------------------------------------------------------

    def list_nodes(self):
        """
        Spark is not a compute cloud like OpenStack/K8s.
        But we can expose worker nodes for monitoring.
        """
        if not self.enabled:
            return []

        status = self.spark.sparkContext.statusTracker()
        executors = status.getExecutorInfos()

        nodes = []
        for exe in executors:
            nodes.append({
                "id": exe.executorId,
                "host": exe.host,
                "status": "active" if exe.totalCores > 0 else "inactive"
            })

        return nodes

    def list_storage(self):
        """
        Spark does not manage storage directly.
        But we can expose input/output dataset status.
        """
        if not self.enabled:
            return []

        return [
            {
                "dataset": "raw_logs",
                "path": self.input_path,
                "exists": True
            },
            {
                "dataset": "spark_processed",
                "path": self.output_path,
                "exists": True
            }
        ]

    def list_network(self):
        """
        Spark does not manage network resources.
        """
        return []

    # ---------------------------------------------------------
    # Spark-specific operations
    # ---------------------------------------------------------

    def process_logs(self):
        """
        Distributed log processing using Spark.
        Reads raw logs, parses them, writes structured parquet.
        """
        if not self.enabled:
            return "Spark disabled"

        df = self.spark.read.text(self.input_path)

        # TODO: Add real parsing logic
        parsed = df.withColumnRenamed("value", "raw_line")

        parsed.write.mode("overwrite").parquet(self.output_path)

        return f"Processed logs → {self.output_path}"

    def heal(self, issue):
        """
        Spark healing logic.
        Example: restart workers, rebalance jobs, clear failed tasks.
        """
        if not self.enabled:
            return "Spark disabled"

        msg = issue.get("message", "").lower()

        if "executor lost" in msg:
            return "Spark executor lost — consider restarting worker nodes"

        if "task failed" in msg:
            return "Spark task failure — rerun job or inspect logs"

        return "Spark issue noted — no automatic action taken"
