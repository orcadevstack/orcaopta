from src.spark.spark_worker import SparkWorker

worker = SparkWorker()

def tool_spark_run_job(job_name: str):
    return worker.run(job_name)

def tool_spark_pipeline(pipeline_name: str):
    return worker.run_pipeline(pipeline_name)

def tool_spark_ingest(source: str):
    return worker.ingest(source)
