"""Rule model."""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Rule(Base):
    """CIS Compliance Rule model."""
    
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    check_expression = Column(String)  # Command/script to check compliance
    severity = Column(String, default="medium")  # low, medium, high, critical
    active = Column(Boolean, default=True)
    
    # Relationship
    violations = relationship("Violation", back_populates="rule")
