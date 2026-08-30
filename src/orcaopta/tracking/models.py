from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    source = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)
    tags = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True)
    family = Column(String)       # anomaly / forecast / autoscale / resource
    version = Column(String)      # v1, v2, v3
    path = Column(String)         # /app/models/anomaly_v2.pkl
    created_at = Column(DateTime, server_default=func.now())
