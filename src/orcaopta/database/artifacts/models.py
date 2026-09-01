from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from orcaopta.database.core.models import Base

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    type = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)
