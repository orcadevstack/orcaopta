from .database import SessionLocal, get_engine
from .models import Event, Metric, Artifact, ModelRegistry


class OrcaoptaTracker:
    """
    Enterprise-grade tracking client for Orcaopta.
    Handles events, metrics, artifacts, and model registry.
    """

    def __init__(self, uri="sqlite:///orcaopta.db"):
        engine = get_engine(uri)
        self.session = SessionLocal(bind=engine)

    # -------------------------------------------------------
    # EVENT TRACKING
    # -------------------------------------------------------
    def log_event(self, type: str, source: str, payload: dict):
        evt = Event(type=type, source=source, payload=payload)
        self.session.add(evt)
        self.session.commit()
        return {"event_id": evt.id, "type": type}

    # -------------------------------------------------------
    # METRIC TRACKING
    # -------------------------------------------------------
    def log_metric(self, name: str, value: float, tags: dict | None = None):
        m = Metric(name=name, value=value, tags=tags or {})
        self.session.add(m)
        self.session.commit()
        return {"metric_id": m.id, "name": name, "value": value}

    # -------------------------------------------------------
    # ARTIFACT TRACKING
    # -------------------------------------------------------
    def log_artifact(self, name: str, path: str):
        a = Artifact(name=name, path=path)
        self.session.add(a)
        self.session.commit()
        return {"artifact_id": a.id, "name": name, "path": path}

    # -------------------------------------------------------
    # MODEL REGISTRY
    # -------------------------------------------------------
    def register_model(self, family: str, version: str, path: str):
        entry = ModelRegistry(family=family, version=version, path=path)
        self.session.add(entry)
        self.session.commit()
        return {
            "model_id": entry.id,
            "family": family,
            "version": version,
            "path": path,
        }
