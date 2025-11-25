import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";
import { FaBug } from "react-icons/fa";

const mockThreats = [
  { indicator: "Malware", count: 5 },
  { indicator: "Phishing", count: 3 },
  { indicator: "Ransomware", count: 2 },
  { indicator: "Brute Force", count: 4 },
  { indicator: "Data Leak", count: 1 },
];

export default function ThreatIndicatorList() {
  return (
    <Card>
      <CardHeader color="#00bfae">
        <FaBug style={{marginRight:8}} /> Threat Indicators
      </CardHeader>
      <CardBody>
        <ul style={{margin:0,padding:0,listStyle:'none'}}>
          {mockThreats.map((t, i) => (
            <li key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'6px 0',borderBottom:i<mockThreats.length-1?'1px solid #eee':'none'}}>
              <span style={{fontWeight:500}}>{t.indicator}</span>
              <span style={{background:'#00bfae',color:'#fff',borderRadius:8,padding:'2px 8px',fontSize:'0.8rem',marginLeft:8}}>{t.count}</span>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
