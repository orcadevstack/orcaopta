"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function GPURealtimeChart() {
  const [data, setData] = useState<any[]>([]);

  async function fetchGPU() {
    const res = await fetch("/api/gpu");
    const json = await res.json();

    setData((prev) => [...prev.slice(-50), {
      timestamp: Date.now(),
      util: json.memory_allocated,
    }]);
  }

  useEffect(() => {
    const interval = setInterval(fetchGPU, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-64 bg-gray-800 p-4 rounded">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="util" stroke="#00cec9" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
