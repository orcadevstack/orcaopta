import argparse
import json
import sys
import requests
import logging

logger = logging.getLogger("orcaopta.mcp.client")

DEFAULT_ENDPOINT = "http://localhost:8000/mcp"


class MCPClient:
    """
    Enterprise MCP client for Orcaopta Cloud Brain.
    Works with the FastAPI MCP server.
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
            logger.error(f"MCP call failed: {tool} - {e}")
            return {"status": "error", "error": str(e)}

    def list_tools(self):
        return self.call("list_tools")


def pretty(obj):
    print(json.dumps(obj, indent=4))


def run_once(client: MCPClient, tool_name: str, args_json: str | None):
    if args_json:
        try:
            args = json.loads(args_json)
        except Exception as e:
            print(f"Invalid JSON arguments: {e}")
            sys.exit(1)
    else:
        args = {}

    result = client.call(tool_name, **args)
    pretty(result)


def run_shell(client: MCPClient):
    print("Orcaopta MCP Shell")
    print("Type tool name or 'exit'. Use JSON for arguments.")
    print("Example: ml_signals")
    print("Example: predict_anomaly {\"records\": [...]}")
    print("--------------------------------------------------")

    while True:
        try:
            line = input("mcp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting MCP shell.")
            break

        if not line:
            continue

        if line in ("exit", "quit"):
            print("Bye.")
            break

        # Parse tool + JSON args
        if " " in line:
            tool, arg_str = line.split(" ", 1)
            try:
                args = json.loads(arg_str)
            except Exception as e:
                print(f"Invalid JSON: {e}")
                continue
        else:
            tool = line
            args = {}

        result = client.call(tool, **args)
        pretty(result)


def main():
    parser = argparse.ArgumentParser(description="Orcaopta MCP CLI")

    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help="MCP endpoint URL (default: http://localhost:8000/mcp)"
    )

    parser.add_argument(
        "--shell",
        action="store_true",
        help="Start interactive MCP shell",
    )

    parser.add_argument(
        "--args",
        help="JSON arguments for the tool",
    )

    parser.add_argument(
        "tool",
        nargs="?",
        help="Tool name to call once",
    )

    args = parser.parse_args()

    client = MCPClient(endpoint=args.endpoint)

    if args.shell:
        run_shell(client)
    elif args.tool:
        run_once(client, args.tool, args.args)
    else:
        print("Available tools:")
        pretty(client.list_tools())


if __name__ == "__main__":
    main()
