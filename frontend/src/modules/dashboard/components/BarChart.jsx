import React from "react";
import { Card, CardHeader, CardBody } from "./UICard";

export default function BarChart() {
  const data = [12, 18, 7, 22, 15, 9, 14];
  const max = Math.max(...data);
  return (
    <Card>
      <CardHeader color="#ff1744">Biểu đồ Cột</CardHeader>
      <CardBody>
        <div style={{display:'flex',alignItems:'flex-end',height:60,gap:6,width:'100%',marginTop:8}}>
          {data.map((v, i) => (
            <div key={i} style={{background:'linear-gradient(180deg,#ffd600 60%,#ff1744 100%)',width:14,borderRadius:'6px 6px 0 0',height:(v/max*80+20)+'%',position:'relative',display:'flex',alignItems:'flex-end',justifyContent:'center',boxShadow:'0 2px 8px #ffd60044'}}>
              <span style={{position:'absolute',bottom:'100%',left:'50%',transform:'translateX(-50%)',fontSize:'0.7rem',color:'#ffd600',marginBottom:2}}>{v}</span>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
