import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function Graphs() {
  const data = [
    { time: "00:00", value: 10 },
    { time: "01:00", value: 30 },
    { time: "02:00", value: 20 },
  ];

  return (
    <>
      <h2>System Metrics</h2>
      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <CartesianGrid stroke="#ccc" />
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
      </LineChart>
    </>
  );
}
