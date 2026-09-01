import { mcpCall } from "@/lib/mcp";

export default async function NodesPage() {
  const announce = await mcpCall("node_announce");
  const peers = await mcpCall("node_list_peers");
  const health = await mcpCall("node_health");
  const metrics = await mcpCall("node_metrics");
  const storage = await mcpCall("node_storage");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">Node Cluster Dashboard</h1>

      <h2 className="text-2xl font-semibold mt-6">Announce</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(announce, null, 2)}
      </pre>

      <h2 className="text-2xl font-semibold mt-6">Peers</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(peers, null, 2)}
      </pre>

      <h2 className="text-2xl font-semibold mt-6">Health</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(health, null, 2)}
      </pre>

      <h2 className="text-2xl font-semibold mt-6">Metrics</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(metrics, null, 2)}
      </pre>

      <h2 className="text-2xl font-semibold mt-6">Storage</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(storage, null, 2)}
      </pre>
    </div>
  );
}
