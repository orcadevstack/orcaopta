FROM bitnami/spark:3.5.1

USER root

# Optional: add Python libs needed for your Spark jobs
RUN pip install pyspark==3.5.1 minio mlflow pandas pyarrow

WORKDIR /app

COPY src /app/src
COPY spark_config.json /app/spark_config.json

CMD ["/opt/bitnami/scripts/spark/entrypoint.sh"]
