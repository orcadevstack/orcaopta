import argparse
import sys
from kitaru.mcp import MCPClient


def run_once(tool_name: str):
    client = MCPClient()
    result = client.call(tool_name)
    print(result)


def run_shell():
    client = MCPClient()
    print("Orcaopta MCP Shell")
    print("Type tool name (or 'exit'):")

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

        try:
            result = client.call(line)
            print(result)
        except Exception as e:
            print(f"Error calling tool '{line}': {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Orcaopta MCP CLI")
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Start interactive MCP shell",
    )
    parser.add_argument(
        "tool",
        nargs="?",
        help="Tool name to call once (omit when using --shell)",
    )

    args = parser.parse_args()

    if args.shell:
        run_shell()
    elif args.tool:
        run_once(args.tool)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
