#!/usr/bin/env bash
set -e

SPARK_MASTER_URL="spark://spark-master:7077"

docker exec -it spark-master spark-submit \
  --master ${SPARK_MASTER_URL} \
  --deploy-mode client \
  --name orcaopta-sre-batch \
  /app/src/spark/pipelines/sre_batch_pipeline.py
