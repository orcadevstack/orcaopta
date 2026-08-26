import React from "react";

export default function SelfHealingTimeline() {
  const events = [
    { time: "03:00", action: "Restarted app due to anomaly" },
    { time: "03:15", action: "Scaled autoscaler to 3 replicas" },
  ];

  return (
    <>
      <h2>Self-Healing Events</h2>
      <ul>
        {events.map((e, i) => (
          <li key={i}>
            <strong>{e.time}</strong>: {e.action}
          </li>
        ))}
      </ul>
    </>
  );
}
