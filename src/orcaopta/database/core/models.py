from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from datetime import datetime

# Base is already defined in orcaopta.database.core.base
from .base import Base


# ---------------------------------------------------------
# Replication Log (cluster + Ceph multi-site)
# ---------------------------------------------------------
class ReplicationLog(Base):
    __tablename__ = "replication_log"

    id = Column(Integer, primary_key=True)
    source_node = Column(String, nullable=False)
    target_node = Column(String, nullable=False)
    status = Column(String, nullable=False)      # "success" / "failed"
    message = Column(String, nullable=True)      # error or info
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
# Enterprise version: includes hashing + size + metadata + versioning
# ---------------------------------------------------------
class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    type = Column(String, nullable=False)
    hash = Column(String, nullable=False)        # SHA256 or BLAKE3
    size_bytes = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=True)
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
