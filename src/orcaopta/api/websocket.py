import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from orcaopta.cloud.apis.detect.graph import build_cloud_graph

router = APIRouter()
logger = logging.getLogger("orcaopta.websocket")

REFRESH_INTERVAL = 2  # seconds


@router.websocket("/ws/cloud-graph")
async def cloud_graph_ws(ws: WebSocket):
    """
    Real-time cloud graph WebSocket stream.
    Sends updated cloud graph every REFRESH_INTERVAL seconds.
    """
    await ws.accept()
    logger.info("WebSocket client connected to /ws/cloud-graph")

    try:
        while True:
            # Build graph (real-time)
            graph = build_cloud_graph()

            # Safe JSON encoding
            try:
                payload = json.dumps(graph)
            except Exception as e:
                logger.error(f"Failed to serialize graph: {e}")
                payload = json.dumps({"error": "serialization_failed"})

            # Send update
            await ws.send_text(payload)

            # Sleep before next update
            await asyncio.sleep(REFRESH_INTERVAL)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from /ws/cloud-graph")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass

    finally:
        logger.info("WebSocket connection closed")
