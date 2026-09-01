
from datetime import datetime
from orcaopta.database.core.session import SessionLocal
from orcaopta.database.core.models import ReplicationLog

def log_replication(source_node: str, target_node: str, status: str, message: str | None = None):
    session = SessionLocal()
    entry = ReplicationLog(
        source_node=source_node,
        target_node=target_node,
        status=status,
        message=message,
        timestamp=datetime.utcnow(),
    )
    session.add(entry)
    session.commit()
    session.close()
