import React from "react";
import { Container, Tabs, Tab } from "@mui/material";
import Graphs from "./components/Graphs";
import VulnTable from "./components/VulnTable";
import SelfHealingTimeline from "./components/SelfHealingTimeline";

export default function App() {
  const [tab, setTab] = React.useState(0);

  return (
    <Container>
      <h1>ORCAOPTA Dashboard</h1>

      <Tabs value={tab} onChange={(e, v) => setTab(v)}>
        <Tab label="Graphs" />
        <Tab label="Vulnerabilities" />
        <Tab label="Self-Healing" />
      </Tabs>

      {tab === 0 && <Graphs />}
      {tab === 1 && <VulnTable />}
      {tab === 2 && <SelfHealingTimeline />}
    </Container>
  );
}
