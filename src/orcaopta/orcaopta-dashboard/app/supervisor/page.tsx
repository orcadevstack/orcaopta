import { mcpCall } from "@/lib/mcp";

export default async function SupervisorPage() {
  const status = await mcpCall("start_supervisor");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">Supervisor</h1>
      <pre className="mt-6 bg-black p-4 rounded text-green-400">
        {JSON.stringify(status, null, 2)}
      </pre>
    </div>
  );
}
