"""Agent model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Agent(Base):
    """Agent (monitored host) model."""
    
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, nullable=False)
    ip_address = Column(String)
    os = Column(String)
    version = Column(String)  # Agent software version
    is_online = Column(Boolean, default=False)
    last_checkin = Column(DateTime(timezone=True), default=func.now())
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    compliance_rate = Column(Float, default=0.0)  
    
    violations = relationship("Violation", back_populates="agent")

