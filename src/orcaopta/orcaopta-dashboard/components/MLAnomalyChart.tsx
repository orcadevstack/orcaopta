"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function MLAnomalyChart({ data }: { data: any[] }) {
  return (
    <div className="h-64 bg-gray-800 p-4 rounded">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="index" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="anomaly" stroke="#e17055" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
