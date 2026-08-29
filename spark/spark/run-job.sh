#!/usr/bin/env bash
set -e

SPARK_MASTER_URL=${SPARK_MASTER_URL:-"spark://spark-master:7077"}

spark-submit \
  --master "${SPARK_MASTER_URL}" \
  --deploy-mode client \
  --name "orcaopta-spark-pipeline" \
  --py-files src \
  src/workers/spark_worker.py
