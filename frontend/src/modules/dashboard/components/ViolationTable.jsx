import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";

const violations = [
  { id: 1, agent: "web-01", rule: "UBU-01", desc: "Disable root SSH login", severity: "high", time: "2025-11-25 10:01" },
  { id: 2, agent: "db-01", rule: "UBU-03", desc: "Ensure auditd enabled", severity: "medium", time: "2025-11-25 09:58" },
  { id: 3, agent: "app-01", rule: "UBU-05", desc: "Password min length", severity: "low", time: "2025-11-25 09:55" },
  { id: 4, agent: "dev-01", rule: "UBU-10", desc: "Disable IPv6", severity: "high", time: "2025-11-25 09:50" },
];

export default function ViolationTable() {
  return (
    <Card>
      <CardHeader color="#ff1744">Bảng Vi Phạm Mới Nhất</CardHeader>
      <CardBody>
        <table style={{width:'100%',borderCollapse:'collapse',fontSize:'1rem',background:'none'}}>
          <thead>
            <tr style={{background:'#23272b'}}>
              <th style={{textAlign:'left',padding:'10px 8px',color:'#ff1744',borderBottom:'2px solid #ff1744',fontWeight:700,letterSpacing:0.5}}>Agent</th>
              <th style={{textAlign:'left',padding:'10px 8px',color:'#ff1744',borderBottom:'2px solid #ff1744',fontWeight:700,letterSpacing:0.5}}>Rule</th>
              <th style={{textAlign:'left',padding:'10px 8px',color:'#ff1744',borderBottom:'2px solid #ff1744',fontWeight:700,letterSpacing:0.5}}>Mô tả</th>
              <th style={{textAlign:'left',padding:'10px 8px',color:'#ff1744',borderBottom:'2px solid #ff1744',fontWeight:700,letterSpacing:0.5}}>Mức độ</th>
              <th style={{textAlign:'left',padding:'10px 8px',color:'#ff1744',borderBottom:'2px solid #ff1744',fontWeight:700,letterSpacing:0.5}}>Thời gian</th>
            </tr>
          </thead>
          <tbody>
            {violations.map((v, i) => (
              <tr key={v.id} style={{borderBottom:'1.5px solid #333',background:i%2?"#23272b":"#181b20",transition:'background 0.2s',cursor:'pointer'}}>
                <td style={{padding:'10px 8px',fontWeight:500,borderRight:'1px solid #222'}}>{v.agent}</td>
                <td style={{padding:'10px 8px',borderRight:'1px solid #222'}}>{v.rule}</td>
                <td style={{padding:'10px 8px',borderRight:'1px solid #222'}}>{v.desc}</td>
                <td style={{padding:'10px 8px',color:v.severity==="high"?'#ff1744':v.severity==="medium"?'#ffd600':'#00e676',fontWeight:700,borderRight:'1px solid #222'}}>{v.severity}</td>
                <td style={{padding:'10px 8px',color:'#888',fontWeight:500}}>{v.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardBody>
    </Card>
  );
}
