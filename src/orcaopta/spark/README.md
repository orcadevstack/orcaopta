###   Orcaopta  

Apache Spark is the **core execution engine** of Orcaopta. It’s responsible for:

- **Distributed computation**  
  All heavy analytics—SLO/SLA calculations, anomaly detection, drift detection, forecasting, RCA—run as parallel jobs across Spark workers, so the platform scales with your cluster size.

- **Batch analytics**  
  Spark batch jobs ingest historical logs and telemetry from S3/MinIO, perform ETL, compute SRE metrics, build failure patterns, train forecasting models, and generate RCA + incident predictions.

- **Streaming analytics**  
  Using **Spark Structured Streaming**, Orcaopta consumes live telemetry from Kafka, detects anomalies and drift in near real‑time, correlates events, and updates incident risk continuously.

- **ML & feature engineering**  
  Spark MLlib is used for:
  - KMeans‑based anomaly detection  
  - Linear regression forecasting  
  - Feature vector assembly for advanced models  
  This keeps all ML workloads distributed and close to the data.

- **Unified engine for SRE logic**  
  Instead of separate tools for batch, streaming, and ML, Orcaopta uses Spark as a single, unified engine:
  - Same codebase for batch + streaming  
  - Same data structures (DataFrames)  
  - Same cluster for analytics, RCA, and remediation signals  

In short: **Spark is the brain and muscle of Orcaopta**—it turns raw telemetry and logs into real‑time insight, predictions, and actions at cloud scale.
