import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";
import { FaBolt } from "react-icons/fa";

const mockAnomalies = [
  { desc: "Đăng nhập bất thường", time: "10:23 12/06" },
  { desc: "Tăng đột biến traffic", time: "09:45 12/06" },
  { desc: "Thay đổi cấu hình lạ", time: "08:30 12/06" },
  { desc: "Tải file nghi vấn", time: "07:50 12/06" },
];

export default function AnomalyList() {
  return (
    <Card>
      <CardHeader color="#ffd600">
        <FaBolt style={{marginRight:8}} /> Bất thường gần đây
      </CardHeader>
      <CardBody>
        <ul style={{margin:0,padding:0,listStyle:'none'}}>
          {mockAnomalies.map((a, i) => (
            <li key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'6px 0',borderBottom:i<mockAnomalies.length-1?'1px solid #eee':'none'}}>
              <span style={{fontWeight:500}}>{a.desc}</span>
              <span style={{color:'#888',fontSize:'0.85rem'}}>{a.time}</span>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
