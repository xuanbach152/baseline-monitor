"""Agent model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
    
    # Relationships
    configurations = relationship("Configuration", back_populates="agent")
    violations = relationship("Violation", back_populates="agent")
    anomaly_history = relationship("AnomalyHistory", back_populates="agent")
