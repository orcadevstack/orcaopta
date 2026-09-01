import Link from "next/link";

export default function Home() {
  const sections = [
    {
      name: "Tools Explorer",
      href: "/tools",
      description: "Browse all MCP tools registered in the Orcaopta backend.",
    },
    {
      name: "Cloud Audits",
      href: "/cloud",
      description: "OpenStack, Kubernetes, and cloud posture analysis.",
    },
    {
      name: "DevOps Audits",
      href: "/devops",
      description: "Terraform plan audits and infrastructure drift detection.",
    },
    {
      name: "ML Signals",
      href: "/ml",
      description: "Anomaly detection, forecasting, autoscale signals.",
    },
    {
      name: "RL Signals",
      href: "/rl",
      description: "Reinforcement learning agent performance metrics.",
    },
    {
      name: "GPU Health",
      href: "/gpu",
      description: "GPU profiler, memory usage, and real-time utilization.",
    },
    {
      name: "Platform Health",
      href: "/platform",
      description: "Ceph cluster health and Kubernetes node statistics.",
    },
    {
      name: "Spark Dashboard",
      href: "/spark",
      description: "Spark jobs, pipelines, ingestion metrics and charts.",
    },
    {
      name: "Node Cluster",
      href: "/nodes",
      description: "Node health, metrics, storage, and peer discovery.",
    },
    {
      name: "Supervisor",
      href: "/supervisor",
      description: "Orcaopta Supervisor status and control.",
    },
  ];

  return (
    <div className="p-10">
      <h1 className="text-5xl font-extrabold text-white">Orcaopta Control Plane</h1>
      <p className="text-gray-400 mt-2 text-lg">
        Unified Cloud • DevOps • ML • RL • GPU • Platform • Spark • Nodes
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-10">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="border border-gray-700 bg-gray-800 p-6 rounded-xl shadow-lg hover:bg-gray-700 transition"
          >
            <h2 className="text-2xl font-bold text-white">{section.name}</h2>
            <p className="text-gray-400 mt-2">{section.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
