import React from "react";

export function Card({ children }) {
  return (
    <div
      className="ui-card"
      style={{
        background: 'linear-gradient(135deg,#23272b 80%,#181b20 100%)',
        borderRadius: 14,
        boxShadow: '0 4px 24px #000c',
        border: '1.5px solid #3a3f47',
        padding: 0,
        margin: 0,
        overflow: 'hidden',
        minHeight: 80,
        color: '#f2f3f7',
      }}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, icon, color }) {
  return (
    <div
      className="ui-card-header"
      style={{
        borderLeft: `5px solid ${color || '#ff1744'}`,
        background: color ? `${color}22` : '#23272b',
        fontWeight: 700,
        fontSize: '1.1rem',
        padding: '14px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        color: color || '#ff1744',
        letterSpacing: 0.2,
        textShadow: '0 2px 8px #000a',
        textTransform: 'none',
      }}
    >
      {icon && <span className="ui-card-icon" style={{ color, fontSize: 22 }}>{icon}</span>}
      <span>{children}</span>
    </div>
  );
}

export function CardBody({ children }) {
  return (
    <div
      className="ui-card-body"
      style={{
        padding: '18px 22px 22px 22px',
        background: 'none',
        minHeight: 60,
        color: '#f2f3f7',
        fontSize: '1.04rem',
      }}
    >
      {children}
    </div>
  );
}
