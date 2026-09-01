from fastapi import APIRouter
from orcaopta.database.core.session import SessionLocal
from orcaopta.database.core.models import NodeState
from datetime import datetime

router = APIRouter()

@router.get("/nodes")
def list_nodes():
    session = SessionLocal()
    nodes = session.query(NodeState).all()
    session.close()
    return {"nodes": [
        {"id": n.node_id, "status": n.status, "last_seen": n.last_seen.isoformat()}
        for n in nodes
    ]}

@router.post("/nodes/register")
def register_node(node_id: str):
    session = SessionLocal()

    existing = session.query(NodeState).filter_by(node_id=node_id).first()
    if existing:
        existing.status = "online"
        existing.last_seen = datetime.utcnow()
    else:
        session.add(NodeState(
            node_id=node_id,
            status="online",
            last_seen=datetime.utcnow()
        ))

    session.commit()
    session.close()
    return {"status": "ok", "node_id": node_id}
