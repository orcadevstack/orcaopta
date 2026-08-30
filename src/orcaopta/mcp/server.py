import logging
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel

# Correct device import
from orcaopta.utils.device import DEVICE

# Supervisor integration
from orcaopta.supervisor.supervisor import start_supervisor

# Load MCP config + mode
from orcaopta.mcp.config import get_mode, load_mcp_config

# MCP tool registry
from orcaopta.mcp.tool import register_tools
from orcaopta.mcp.tools_node import *
from orcaopta.mcp.tools_blockchain import *
from orcaopta.mcp.tools_spark import *

logger = logging.getLogger("orcaopta.mcp")


# ============================================================
# MCP Core
# ============================================================

class MCPRequest(BaseModel):
    tool: str
    arguments: dict | None = None


class MCPServer:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, func, description: str = ""):
        self.tools[name] = {
            "func": func,
            "description": description,
        }
        logger.info(f"[MCP] Tool registered: {name} - {description}")

    def list_tools(self):
        return [
            {"name": name, "description": meta["description"]}
            for name, meta in self.tools.items()
        ]

    def handle(self, request: MCPRequest):
        name = request.tool
        args = request.arguments or {}

        if name == "list_tools":
            return {"status": "ok", "tools": self.list_tools()}

        if name not in self.tools:
            return {"status": "error", "error": f"Unknown tool: {name}"}

        func = self.tools[name]["func"]

        try:
            result = func(**args)
            return {"status": "ok", "tool": name, "result": result}
        except Exception as e:
            logger.error(f"[MCP] Tool '{name}' failed: {e}")
            return {"status": "error", "error": str(e)}


# ============================================================
# Banner
# ============================================================

def print_banner():
    banner = r"""
  ____   ____   ____    ___    ____   ____   _______ 
  / __ \ / __ \ / __ \  / _ \  / __ \ / __ \ |__   __|
 | |  | | |  | | |  | |/ /_\ \| |  | | |  | |   | |   
 | |  | | |  | | |  | ||  _  || |  | | |  | |   | |   
 | |__| | |__| | |__| || | | || |__| | |__| |   | |   
  \___\_\\____/ \____/ |_| |_|\____/ \____/    |_|   

    Orcaopta Control Plane - Enterprise MCP Server
    """
    print(banner)


# ============================================================
# FastAPI App
# ============================================================

def create_app():
    print_banner()

    # Load enterprise MCP config
    mcp_cfg = load_mcp_config()
    mode = get_mode()

    logger.info(f"[MCP] Mode: {mode}")
    logger.info(f"[MCP] Config Loaded: {mcp_cfg}")
    logger.info(f"[MCP] Device: {DEVICE.upper()}")

    app = FastAPI(
        title="Orcaopta Control Plane",
        description="Unified MCP + ML + RL + Cloud Audit backend",
        version="1.0.0",
    )

    # Create MCP server
    mcp = MCPServer()

    # Register all MCP tools
    register_tools(mcp)

    # Include P2P router AFTER app is created
    from orcaopta.p2p.router import router as p2p_router
    app.include_router(p2p_router)

    # MCP endpoint
    @app.post("/v1/mcp")
    async def mcp_endpoint(request: MCPRequest):
        return mcp.handle(request)

    # Health endpoint
    @app.get("/v1/health")
    async def health():
        return {
            "status": "ok",
            "service": "orcaopta-mcp",
            "mode": mode,
            "device": DEVICE,
        }

    return app


# ============================================================
# Entrypoint
# ============================================================

def main():
    import uvicorn

    logger.info("[MCP] Starting Orcaopta MCP Server...")
    logger.info(f"[MCP] Device selected: {DEVICE.upper()}")

    # Start supervisor (autoscale + metrics)
    start_supervisor(interval=10)

    app = create_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
