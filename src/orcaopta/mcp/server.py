import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from orcaopta.utils.device import DEVICE
from orcaopta.supervisor.supervisor import start_supervisor
from orcaopta.mcp.config import get_mode, load_mcp_config

from orcaopta.mcp.tool import register_tools
from orcaopta.ai.llm import llm

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
        self.tools[name] = {"func": func, "description": description}
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
# ASCII Banner
# ============================================================

BANNER = r"""
  ____   ____   ____    ___    ____   ____   _______
  / __ \ / __ \ / __ \  / _ \  / __ \ / __ \ |__   __|
 | |  | | |  | | |  | |/ /_\ \| |  | | |  | |   | |
 | |  | | |  | | |  | ||  _  || |  | | |  | |   | |
 | |__| | |__| | |__| || | | || |__| | |__| |   | |
  \___\_\\____/ \____/ |_| |_|\____/ \____/    |_|

        Orcaopta Control Plane — Enterprise MCP Server
"""


# ============================================================
# FastAPI App
# ============================================================

def create_app():
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

    # ============================================================
    # LLM Tools
    # ============================================================

    def tool_llm(prompt: str, model: str = None):
        return {"response": llm.run(prompt, model=model)}

    def tool_llm_stream(prompt: str, model: str = None):
        output = ""
        for token in llm.stream(prompt, model=model):
            output += token
        return {"response": output}

    def tool_llm_route(task: str, prompt: str):
        return {"response": llm.route(task, prompt)}

    def tool_llm_tools(prompt: str):
        return llm.run_with_tools(prompt, mcp.tools)

    mcp.register("llm", tool_llm, "LLM text generation")
    mcp.register("llm_stream", tool_llm_stream, "LLM streaming output")
    mcp.register("llm_route", tool_llm_route, "LLM routing engine")
    mcp.register("llm_tools", tool_llm_tools, "LLM tool-calling JSON interface")

    # ============================================================
    # Homepage (like Ollama)
    # ============================================================

    @app.get("/", response_class=HTMLResponse)
    def home():
        return f"""
        <html>
        <body style="font-family: monospace; background: #111; color: #0f0;">
        <pre>{BANNER}</pre>
        <h3>Status: Running</h3>
        <p>Mode: {mode}</p>
        <p>Device: {DEVICE.upper()}</p>
        <p>Tools Registered: {len(mcp.tools)}</p>
        </body>
        </html>
        """

    # ============================================================
    # Info Endpoint
    # ============================================================

    @app.get("/v1/info")
    def info():
        return {
            "service": "Orcaopta Control Plane",
            "version": "1.0.0",
            "mode": mode,
            "device": DEVICE,
            "tools": list(mcp.tools.keys()),
        }

    # ============================================================
    # Health Endpoint
    # ============================================================

    @app.get("/v1/health")
    def health():
        return {
            "status": "ok",
            "service": "orcaopta-mcp",
            "mode": mode,
            "device": DEVICE,
        }

    # ============================================================
    # MCP Endpoint
    # ============================================================

    @app.post("/v1/mcp")
    async def mcp_endpoint(request: MCPRequest):
        return mcp.handle(request)

    # ============================================================
    # Supervisor Startup (FastAPI lifespan-safe)
    # ============================================================

    @app.on_event("startup")
    async def startup_event():
        logger.info("[MCP] Starting Supervisor...")
        start_supervisor(interval=10)

    return app


# ============================================================
# Entrypoint
# ============================================================

def main():
    import uvicorn

    logger.info("[MCP] Starting Orcaopta MCP Server...")
    logger.info(f"[MCP] Device selected: {DEVICE.upper()}")

    app = create_app()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
