import { mcpCall } from "@/lib/mcp";

export default async function RLPage() {
  const rl = await mcpCall("rl_signals");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">RL Signals</h1>
      <pre className="mt-6 bg-black p-4 rounded text-green-400">
        {JSON.stringify(rl, null, 2)}
      </pre>
    </div>
  );
}
