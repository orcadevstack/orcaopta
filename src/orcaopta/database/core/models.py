from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    JSON,
    Boolean,
    LargeBinary,
)

from orcaopta.core.base import Base


# ---------------------------------------------------------
# Replication Log (cluster + Ceph multi-site)
# ---------------------------------------------------------
class ReplicationLog(Base):
    __tablename__ = "replication_log"

    id = Column(Integer, primary_key=True)
    source_node = Column(String, nullable=False)
    target_node = Column(String, nullable=False)
    status = Column(String, nullable=False)      # "success" / "failed"
    message = Column(LargeBinary, nullable=True) # encrypted
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# Metrics (generic ML/RL/GPU/Spark metrics)
# ---------------------------------------------------------
class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# GPU Profiler
# ---------------------------------------------------------
class GPUUsage(Base):
    __tablename__ = "gpu_usage"

    id = Column(Integer, primary_key=True)
    utilization = Column(Float, nullable=True)
    memory_allocated = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# RL Agent Rewards
# ---------------------------------------------------------
class RLReward(Base):
    __tablename__ = "rl_rewards"

    id = Column(Integer, primary_key=True)
    episode = Column(Integer, nullable=False)
    reward = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# Spark Job Metadata
# ---------------------------------------------------------
class SparkJob(Base):
    __tablename__ = "spark_jobs"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    stages = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# Artifact Index (models, checkpoints, logs)
# Enterprise version: hashing + size + meta + versioning
# ---------------------------------------------------------
class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    type = Column(String, nullable=False)
    hash = Column(String, nullable=False)        # SHA256 or BLAKE3
    size_bytes = Column(Integer, nullable=False)
    meta = Column(LargeBinary, nullable=True)    # encrypted
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# Node State (cluster replication)
# ---------------------------------------------------------
class NodeState(Base):
    __tablename__ = "node_state"

    id = Column(Integer, primary_key=True)
    node_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# OTS Run (experiment / session)
# ---------------------------------------------------------
class OTSRun(Base):
    __tablename__ = "ots_runs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="running", nullable=False)  # running / completed / failed
    meta = Column(LargeBinary, nullable=True)                   # encrypted


# ---------------------------------------------------------
# OTS Metrics (per run, key/value)
# ---------------------------------------------------------
class OTSMetric(Base):
    __tablename__ = "ots_metrics"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, nullable=False, index=True)
    key = Column(String, nullable=False)
    value = Column(LargeBinary, nullable=True)   # encrypted
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# OTS Events (structured logs / decisions / anomalies)
# ---------------------------------------------------------
class OTSEvent(Base):
    __tablename__ = "ots_events"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(LargeBinary, nullable=True) # encrypted
    severity = Column(String, default="info", nullable=False)  # info / warn / error / critical
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------
# OTS Artifacts (models, checkpoints, logs)
# ---------------------------------------------------------
class OTSArtifact(Base):
    __tablename__ = "ots_artifacts"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, nullable=False, index=True)
    artifact_id = Column(String, unique=True, nullable=False)
    path = Column(String, nullable=False)
    type = Column(String, nullable=False)        # model / checkpoint / log / config
    hash = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    meta = Column(LargeBinary, nullable=True)    # encrypted
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
