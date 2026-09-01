import { mcpCall } from "@/lib/mcp";

export default async function DevOpsPage() {
  const terraform = await mcpCall("terraform_audit");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">DevOps Audits</h1>
      <pre className="mt-6 bg-black p-4 rounded text-green-400">
        {JSON.stringify(terraform, null, 2)}
      </pre>
    </div>
  );
}
