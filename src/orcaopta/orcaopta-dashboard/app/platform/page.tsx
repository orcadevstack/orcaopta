import { mcpCall } from "@/lib/mcp";

export default async function PlatformPage() {
  const ceph = await mcpCall("platform.ceph.health");
  const nodes = await mcpCall("platform.k8s.nodes");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">Platform Health</h1>
      <pre className="mt-6 bg-black p-4 rounded">
        {JSON.stringify({ ceph, nodes }, null, 2)}
      </pre>
    </div>
  );
}
