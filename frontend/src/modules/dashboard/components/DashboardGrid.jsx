import React from "react";
import StatCards from "./StatCards";
import AgentTable from "./AgentTable";
import ViolationTable from "./ViolationTable";
import ComplianceChart from "./ComplianceChart";
import DonutChart from "./DonutChart";
import BarChart from "./BarChart";
import RiskyUserList from "./RiskyUserList";
import ThreatIndicatorList from "./ThreatIndicatorList";
import AnomalyList from "./AnomalyList";

export default function DashboardGrid() {
  // Mock stats data
  const stats = {
    totalAgents: 10,
    onlineAgents: 8,
    complianceRate: 72.5,
    totalViolations: 15,
  };
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(12, 1fr)',
        gridAutoRows: 'minmax(120px, auto)',
        gap: 36,
        padding: 36,
        background: '#181b20',
        minHeight: '100vh',
        width: '100vw',
        boxSizing: 'border-box',
        maxWidth: '100vw',
      }}
    >
      {/* Stat cards row ngang */}
      <div style={{ gridColumn: '1/13', gridRow: '1', marginBottom: 8 }}>
        <StatCards stats={stats} />
      </div>
      {/* Main charts */}
      <div style={{ gridColumn: '1/7', gridRow: '2' }}>
        <ComplianceChart />
      </div>
      <div style={{ gridColumn: '7/11', gridRow: '2' }}>
        <BarChart />
      </div>
      <div style={{ gridColumn: '11/13', gridRow: '2' }}>
        <DonutChart />
      </div>
      {/* Tables */}
      <div style={{ gridColumn: '1/7', gridRow: '3' }}>
        <AgentTable />
      </div>
      <div style={{ gridColumn: '7/13', gridRow: '3' }}>
        <ViolationTable />
      </div>
      {/* Lists */}
      <div style={{ gridColumn: '1/5', gridRow: '4' }}>
        <RiskyUserList />
      </div>
      <div style={{ gridColumn: '5/9', gridRow: '4' }}>
        <ThreatIndicatorList />
      </div>
      <div style={{ gridColumn: '9/13', gridRow: '4' }}>
        <AnomalyList />
      </div>
    </div>
  );
}
