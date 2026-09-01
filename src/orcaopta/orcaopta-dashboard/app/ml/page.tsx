import { mcpCall } from "@/lib/mcp";

export default async function CloudPage() {
  const graph = await mcpCall("cloud.graph");
  const openstack = await mcpCall("cloud.openstack.audit");
  const k8s = await mcpCall("cloud.kubernetes.audit");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">Cloud Audits</h1>
      <pre className="mt-6 bg-black p-4 rounded">
        {JSON.stringify({ graph, openstack, k8s }, null, 2)}
      </pre>
    </div>
  );
}
