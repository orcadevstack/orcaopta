"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function RLPerformanceChart({ data }: { data: any[] }) {
  return (
    <div className="h-64 bg-gray-800 p-4 rounded">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="episode" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="reward" stroke="#fdcb6e" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
