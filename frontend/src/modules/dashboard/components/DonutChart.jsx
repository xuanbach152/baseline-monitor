import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";

export default function DonutChart() {
  return (
    <Card>
      <CardHeader color="#29b6f6">Tỷ lệ trạng thái</CardHeader>
      <CardBody>
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="#23272b" stroke="#333" strokeWidth="4" />
          <path d="M50 10 A40 40 0 1 1 10 50" stroke="#ffd600" strokeWidth="10" fill="none" />
          <path d="M10 50 A40 40 0 0 1 50 10" stroke="#00e676" strokeWidth="10" fill="none" />
          <path d="M50 90 A40 40 0 0 1 90 50" stroke="#ff1744" strokeWidth="10" fill="none" />
        </svg>
        <div style={{display:'flex',justifyContent:'center',gap:8,marginTop:8}}>
          <span style={{color:'#ffd600'}}>PASS</span>
          <span style={{color:'#00e676'}}>ONLINE</span>
          <span style={{color:'#ff1744'}}>FAIL</span>
        </div>
      </CardBody>
    </Card>
  );
}
