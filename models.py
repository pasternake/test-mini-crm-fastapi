from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class SourceOperatorLink(Base):
    __tablename__ = "source_operator_links"
    source_id = Column(Integer, ForeignKey("sources.id"), primary_key=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), primary_key=True)
    weight = Column(Integer, default=0)

    operator = relationship("Operator", back_populates="source_links")
    source = relationship("Source", back_populates="operator_links")

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    load_limit = Column(Integer, default=10)

    source_links = relationship("SourceOperatorLink", back_populates="operator")
    interactions = relationship("Interaction", back_populates="operator")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    operator_links = relationship("SourceOperatorLink", back_populates="source")
    interactions = relationship("Interaction", back_populates="source")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True) # e.g. email or phone

    interactions = relationship("Interaction", back_populates="lead")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="OPEN") # OPEN, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="interactions")
    source = relationship("Source", back_populates="interactions")
    operator = relationship("Operator", back_populates="interactions")
