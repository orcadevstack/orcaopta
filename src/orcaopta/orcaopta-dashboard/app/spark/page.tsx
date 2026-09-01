import { mcpCall } from "@/lib/mcp";

export default async function SparkPage() {
  const runJob = await mcpCall("spark_run_job");
  const pipeline = await mcpCall("spark_pipeline");
  const ingest = await mcpCall("spark_ingest");

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">Spark Dashboard</h1>

      <h2 className="text-2xl font-semibold mt-6">Run Job</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(runJob, null, 2)}
      </pre>

      <h2 className="text-2xl font-semibold mt-6">Pipeline</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(pipeline, null, 2)}
      </pre>

      <h2 className="text-2xl font-semibold mt-6">Ingestion</h2>
      <pre className="mt-2 bg-black p-4 rounded text-green-400">
        {JSON.stringify(ingest, null, 2)}
      </pre>
    </div>
  );
}
