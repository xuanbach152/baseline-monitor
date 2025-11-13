"""Violation model"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    rule_id = Column(Integer, ForeignKey("rules.id"))
    message = Column(String)
    confidence_score = Column(Float)  # mức độ chắc chắn (0–1)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="violations")
    rule = relationship("Rule", back_populates="violations")
