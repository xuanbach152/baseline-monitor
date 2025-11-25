import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";

const agents = [
  { id: 1, hostname: "web-01", ip: "10.21.10.19", status: "online", compliance: 90 },
  { id: 2, hostname: "db-01", ip: "10.21.10.20", status: "offline", compliance: 60 },
  { id: 3, hostname: "app-01", ip: "10.21.10.228", status: "online", compliance: 80 },
  { id: 4, hostname: "proxy-01", ip: "10.21.10.137", status: "online", compliance: 100 },
  { id: 5, hostname: "dev-01", ip: "10.21.10.140", status: "offline", compliance: 50 },
];

export default function AgentTable() {
  return (
    <Card>
      <CardHeader color="#00e676">Danh sách Agent</CardHeader>
      <CardBody>
        <table className="agent-table">
          <thead>
            <tr>
              <th>Hostname</th>
              <th>IP</th>
              <th>Trạng thái</th>
              <th>Compliance (%)</th>
            </tr>
          </thead>
          <tbody>
            {agents.map(agent => (
              <tr key={agent.id} className={agent.status === "online" ? "online-row" : "offline-row"}>
                <td>{agent.hostname}</td>
                <td>{agent.ip}</td>
                <td>
                  <span className={`status-dot ${agent.status}`}></span>
                  {agent.status}
                </td>
                <td>{agent.compliance}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardBody>
    </Card>
  );
}
