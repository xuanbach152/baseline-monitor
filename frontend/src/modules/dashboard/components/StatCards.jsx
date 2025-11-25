import React from "react";
import StatCard from "./StatCard";
import { AiOutlineUser, AiOutlineCheckCircle, AiOutlineWarning, AiOutlineBug } from "react-icons/ai";

export default function StatCards({ stats }) {
  return (
    <div
      className="stat-cards-row"
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 28,
        width: '100%',
        minWidth: 0,
        margin: 0,
      }}
    >
      <StatCard label="Tổng số Agent" value={stats.totalAgents} icon={<AiOutlineUser />} color="#00e676" />
      <StatCard label="Agent Online" value={stats.onlineAgents} icon={<AiOutlineCheckCircle />} color="#29b6f6" />
      <StatCard label="Tỷ lệ Compliance" value={stats.complianceRate + '%'} icon={<AiOutlineWarning />} color="#ffd600" />
      <StatCard label="Tổng số Vi phạm" value={stats.totalViolations} icon={<AiOutlineBug />} color="#ff1744" />
    </div>
  );
}
