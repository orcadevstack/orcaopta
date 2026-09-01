export default function MCPToolCard({ name, meta }: { name: string; meta: any }) {
  return (
    <div className="border border-gray-700 bg-gray-800 p-4 rounded-lg shadow hover:bg-gray-700 transition">
      <h2 className="text-xl font-bold text-white">{name}</h2>

      <p className="text-gray-400 mt-2">
        {meta.description || "No description available"}
      </p>

      <div className="mt-3">
        <span className="text-sm text-blue-400">
          Category: {meta.category || "uncategorized"}
        </span>
      </div>

      <div className="mt-2 text-sm text-gray-500">
        Params: {JSON.stringify(meta.params || {}, null, 2)}
      </div>
    </div>
  );
}
