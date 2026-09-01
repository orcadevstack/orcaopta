import os
from ..core.session import SessionLocal
from .models import Artifact

def index_artifact(path, type):
    session = SessionLocal()
    session.add(Artifact(path=path, type=type))
    session.commit()
    session.close()
