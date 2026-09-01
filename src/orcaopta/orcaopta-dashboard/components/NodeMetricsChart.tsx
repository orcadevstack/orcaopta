"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function NodeMetricsChart() {
  const [data, setData] = useState<any[]>([]);

  async function fetchMetrics() {
    const res = await fetch("/api/node-metrics");
    const json = await res.json();

    setData((prev) => [...prev.slice(-50), {
      timestamp: Date.now(),
      cpu: json.cpu_usage,
      mem: json.memory_usage,
    }]);
  }

  useEffect(() => {
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-64 bg-gray-800 p-4 rounded">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="cpu" stroke="#ff7675" />
          <Line type="monotone" dataKey="mem" stroke="#74b9ff" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
