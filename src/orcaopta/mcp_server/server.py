import logging
from kitaru.mcp import MCPServer
from src.orcaopta.mcp import worker
from src.orcaopta.mcp_server.banner import print_banner

# GPU health tool
from orcaopta.utils.device import device
import torch

logger = logging.getLogger("orcaopta.mcp")


def create_app():
    """
    Create the unified Orcaopta backend app.
    MCP + Tools + Supervisor all run inside one FastAPI server.
    """
    print_banner()

    app = FastAPI(
        title="Orcaopta Control Plane",
        description="Unified MCP + ML + RL + Cloud Audit backend",
        version="1.0.0",
    )


    mcp = MCPServer()
    register_tools(mcp)  # Load all MCP tools

    @app.post("/mcp")
    async def mcp_endpoint(request: dict):
        """
        Main MCP endpoint.
        All notebook buttons call this endpoint.
        """
        return mcp.handle(request)


    supervisor = Supervisor()

    @app.post("/supervisor/start")
    async def start_supervisor():
        supervisor.start()
        return {"status": "supervisor_started"}


    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "orcaopta"}

    return app


def main():
    import uvicorn
    app = create_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def gpu_health():
    """
    MCP tool: returns GPU or CPU status.
    """
    if device == "cuda":
        try:
            gpu_name = torch.cuda.get_device_name(0)
            capability = torch.cuda.get_device_capability(0)
            total_mem = torch.cuda.get_device_properties(0).total_memory
            allocated = torch.cuda.memory_allocated()
            reserved = torch.cuda.memory_reserved()

            return {
                "status": "healthy",
                "device": "cuda",
                "gpu_name": gpu_name,
                "capability": capability,
                "memory_total": total_mem,
                "memory_allocated": allocated,
                "memory_reserved": reserved,
            }
        except Exception as e:
            logger.error(f"GPU health check failed: {e}")
            return {
                "status": "error",
                "device": "cuda",
                "message": str(e)
            }

    # CPU fallback
    return {
        "status": "cpu-mode",
        "device": "cpu",
        "message": "GPU not available"
    }


def main():
    # Startup banner
    print_banner()

    logger.info("Starting Orcaopta MCP Server...")
    logger.info(f"Device selected: {device.upper()}")

    # Initialize MCP worker
    w = worker()

    # Register GPU health tool
    w.tool(gpu_health)

    # Start MCP server
    server = MCPServer(w)
    server.run()


if __name__ == "__main__":
    main()
