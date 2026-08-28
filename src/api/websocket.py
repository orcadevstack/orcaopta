from fastapi import APIRouter, WebSocket
import asyncio, json
from src.graph.engine import OrcaGraphEngine

router = APIRouter()

@router.websocket("/ws/cloud-graph")
async def cloud_graph_ws(ws: WebSocket):
    await ws.accept()
    while True:
        graph = get_cloud_graph()  # your engine
        await ws.send_text(json.dumps(graph))
        await asyncio.sleep(2)
