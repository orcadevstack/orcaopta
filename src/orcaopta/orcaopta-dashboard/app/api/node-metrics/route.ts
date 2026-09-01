import { NextResponse } from "next/server";

export async function GET() {
  const res = await fetch("http://localhost:8000/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      method: "tools.call",
      params: { name: "node_metrics", args: {} }
    }),
  });

  const json = await res.json();
  return NextResponse.json(json);
}
