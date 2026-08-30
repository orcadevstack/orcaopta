from fastapi import APIRouter
from src.orcaopta.p2p.protocol import (
    handle_health_update,
    handle_autoscale_proposal,
    handle_autoscale_vote,
)

router = APIRouter(prefix="/p2p")

@router.post("/health")
def p2p_health(payload: dict):
    return handle_health_update(payload)

@router.post("/autoscale/proposal")
def p2p_proposal(payload: dict):
    return handle_autoscale_proposal(payload)

@router.post("/autoscale/vote")
def p2p_vote(payload: dict):
    return handle_autoscale_vote(payload)
