import MCPToolCard from "./MCPToolCard";

export default function MCPToolGrid({ tools }: { tools: any }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      {Object.entries(tools).map(([name, meta]: any) => (
        <MCPToolCard key={name} name={name} meta={meta} />
      ))}
    </div>
  );
}
