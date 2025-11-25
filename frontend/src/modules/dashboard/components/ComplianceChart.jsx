import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";

export default function ComplianceChart() {
  // Dữ liệu mock
  return (
    <Card>
      <CardHeader color="#ffd600">Biểu đồ Compliance</CardHeader>
      <CardBody>
        <svg width="100%" height="100" viewBox="0 0 320 100">
          <polyline fill="none" stroke="#ffd600" strokeWidth="3" points="0,80 40,60 80,40 120,50 160,20 200,40 240,10 280,30 320,10" />
          <polyline fill="none" stroke="#ff1744" strokeWidth="2" points="0,90 40,70 80,80 120,60 160,70 200,50 240,60 280,40 320,20" />
        </svg>
      </CardBody>
    </Card>
  );
}
