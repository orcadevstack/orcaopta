import { mcpCall } from "@/lib/mcp";
import GPUUsageChart from "@/components/GPUUsageChart";

export default async function GPUPage() {
  const health = await mcpCall("gpu_profiler");

  const chartData =
    health?.metrics?.map((m: any) => ({
      timestamp: m.timestamp,
      utilization: m.utilization,
    })) ?? [];

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">GPU Health</h1>

      <div className="mt-6">
        <GPUUsageChart data={chartData} />
      </div>

      <pre className="mt-6 bg-black p-4 rounded text-green-400">
        {JSON.stringify(health, null, 2)}
      </pre>
    </div>
  );
}
