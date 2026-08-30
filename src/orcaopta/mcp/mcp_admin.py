import argparse
import json
import sys
import requests
import logging

logger = logging.getLogger("orcaopta.mcp.admin")

DEFAULT_ENDPOINT = "http://localhost:8000/mcp"


class MCPAdmin:
    """
    Enterprise MCP Admin Client for Orcaopta Cloud Brain.
    Provides:
      - Supervisor control
      - Model reload
      - Cache clearing
      - Tool listing
      - Health checks
    """

    def __init__(self, endpoint: str = DEFAULT_ENDPOINT):
        self.endpoint = endpoint

    def call(self, tool: str, **arguments):
        payload = {
            "tool": tool,
            "arguments": arguments or {}
        }

        try:
            resp = requests.post(self.endpoint, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"MCP admin call failed: {tool} - {e}")
            return {"status": "error", "error": str(e)}

    def list_tools(self):
        return self.call("list_tools")

    # ---------------------------------------------------------
    # Supervisor Controls
    # ---------------------------------------------------------

    def restart_supervisor(self):
        return self.call("start_supervisor")

    # ---------------------------------------------------------
    # Model Controls
    # ---------------------------------------------------------

    def reload_models(self):
        return self.call("reload_models")

    def clear_model_cache(self):
        return self.call("clear_model_cache")

    # ---------------------------------------------------------
    # Health Checks
    # ---------------------------------------------------------

    def health(self):
        return self.call("system_mode")

    # ---------------------------------------------------------
    # Cloud Audits
    # ---------------------------------------------------------

    def audit_openstack(self):
        return self.call("openstack_audit")

    def audit_kubernetes(self):
        return self.call("kubernetes_audit")

    def audit_terraform(self):
        return self.call("terraform_audit")

    def cloud_graph(self):
        return self.call("cloud_graph")


# ============================================================
# CLI UTILITIES
# ============================================================

def pretty(obj):
    print(json.dumps(obj, indent=4))


def main():
    parser = argparse.ArgumentParser(description="Orcaopta MCP Admin CLI")

    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help="MCP endpoint URL (default: http://localhost:8000/mcp)"
    )

    sub = parser.add_subparsers(dest="command")

    # Supervisor
    sub.add_parser("restart-supervisor", help="Restart the Orcaopta Supervisor")

    # Models
    sub.add_parser("reload-models", help="Reload all ML models")
    sub.add_parser("clear-cache", help="Clear ML model cache")

    # Health
    sub.add_parser("health", help="Show MCP system health")

    # Cloud audits
    sub.add_parser("audit-openstack", help="Run OpenStack audit")
    sub.add_parser("audit-k8s", help="Run Kubernetes audit")
    sub.add_parser("audit-terraform", help="Run Terraform audit")
    sub.add_parser("cloud-graph", help="Show cloud graph")

    # Tools
    sub.add_parser("list-tools", help="List all MCP tools")

    # Raw tool call
    raw = sub.add_parser("call", help="Call any MCP tool")
    raw.add_argument("tool", help="Tool name")
    raw.add_argument("--args", help="JSON arguments")

    args = parser.parse_args()
    admin = MCPAdmin(endpoint=args.endpoint)

    # ---------------------------------------------------------
    # Command Routing
    # ---------------------------------------------------------

    if args.command == "restart-supervisor":
        pretty(admin.restart_supervisor())

    elif args.command == "reload-models":
        pretty(admin.reload_models())

    elif args.command == "clear-cache":
        pretty(admin.clear_model_cache())

    elif args.command == "health":
        pretty(admin.health())

    elif args.command == "audit-openstack":
        pretty(admin.audit_openstack())

    elif args.command == "audit-k8s":
        pretty(admin.audit_kubernetes())

    elif args.command == "audit-terraform":
        pretty(admin.audit_terraform())

    elif args.command == "cloud-graph":
        pretty(admin.cloud_graph())

    elif args.command == "list-tools":
        pretty(admin.list_tools())

    elif args.command == "call":
        if args.args:
            try:
                arguments = json.loads(args.args)
            except Exception as e:
                print(f"Invalid JSON: {e}")
                sys.exit(1)
        else:
            arguments = {}

        pretty(admin.call(args.tool, **arguments))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
