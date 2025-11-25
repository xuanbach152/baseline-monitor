import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";

export default function StatCard({ label, value, icon, color }) {
  return (
    <Card>
      <CardHeader icon={icon} color={color}>{label}</CardHeader>
      <CardBody>
        <div className="stat-value" style={{ color }}>{value}</div>
      </CardBody>
    </Card>
  );
}
