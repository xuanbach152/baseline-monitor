import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";
import { FaExclamationTriangle } from "react-icons/fa";

const mockUsers = [
  { name: "Nguyen Van A", risk: "Cao", count: 7 },
  { name: "Tran Thi B", risk: "Trung bình", count: 4 },
  { name: "Le Van C", risk: "Cao", count: 6 },
  { name: "Pham Thi D", risk: "Thấp", count: 2 },
  { name: "Hoang Van E", risk: "Trung bình", count: 3 },
];

export default function RiskyUserList() {
  return (
    <Card>
      <CardHeader color="#ff9800">
        <FaExclamationTriangle style={{marginRight:8}} /> Người dùng rủi ro
      </CardHeader>
      <CardBody>
        <ul style={{margin:0,padding:0,listStyle:'none'}}>
          {mockUsers.map((u, i) => (
            <li
              key={i}
              style={{
                display:'flex',alignItems:'center',justifyContent:'space-between',
                padding:'10px 0',
                borderBottom:i<mockUsers.length-1?'2px solid #333':'none',
                background:i%2?"#23272b":"#181b20",
                transition:'background 0.2s',
                cursor:'pointer',
              }}
            >
              <span style={{fontWeight:600,fontSize:'1.05rem',color:'#fff'}}>{u.name}</span>
              <span style={{color:u.risk==="Cao"?'#ff1744':u.risk==="Trung bình"?'#ff9800':'#00bfae',fontWeight:700,fontSize:'1.05rem'}}>{u.risk}</span>
              <span style={{background:'#ff1744',color:'#fff',borderRadius:8,padding:'3px 12px',fontSize:'1.1rem',marginLeft:8,fontWeight:700,boxShadow:'0 2px 8px #ff174488'}}>{u.count}</span>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
