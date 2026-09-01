export async function mcpCall(tool: string, args: any = {}) {
  const res = await fetch("http://localhost:8000/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      method: "tools.call",
      params: { name: tool, args }
    }),
    cache: "no-store"
  });

  return res.json();
}

export async function mcpListTools() {
  const res = await fetch("http://localhost:8000/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      method: "tools.list",
      params: {}
    }),
    cache: "no-store"
  });

  return res.json();
}
