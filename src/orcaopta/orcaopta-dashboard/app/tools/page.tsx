import { mcpListTools } from "@/lib/mcp";

export default async function ToolsPage() {
  const tools = await mcpListTools();

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">MCP Tools</h1>

      <div className="grid grid-cols-2 gap-6">
        {Object.entries(tools.tools).map(([name, meta]: any) => (
          <div key={name} className="border p-4 rounded bg-gray-800">
            <h2 className="text-xl font-bold">{name}</h2>
            <p className="text-gray-400">{meta.description}</p>
            <p className="text-sm text-blue-400 mt-2">Category: {meta.category}</p>
            <p className="text-sm text-gray-500">Params: {JSON.stringify(meta.params)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
