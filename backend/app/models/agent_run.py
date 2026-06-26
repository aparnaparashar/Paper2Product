"""
Agent Traceability Table
Every agent execution is stored here so we can answer:
"How did the Judge Agent reach score 8.4/10?"
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, JSON, ForeignKey
from app.core.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id     = Column(String, ForeignKey("projects.id"), nullable=False, index=True)

    # Identity
    agent_name     = Column(String, nullable=False)    # e.g. "market_discovery"
    agent_label    = Column(String, nullable=True)     # e.g. "Market Discovery"
    model_used     = Column(String, nullable=True)     # e.g. "gemini-2.5-flash"
    model_provider = Column(String, nullable=True)     # "google-gemini" | "groq"

    # Traceability (Feature 1 + 6)
    output         = Column(JSON, nullable=True)       # structured agent output
    reasoning      = Column(JSON, nullable=True)       # list of reasoning steps
    confidence     = Column(Float, nullable=True)      # 0.0 – 1.0
    sources        = Column(JSON, nullable=True)       # source citations list

    # Evaluation metrics (Feature 9)
    started_at        = Column(DateTime, nullable=True)
    completed_at      = Column(DateTime, nullable=True)
    duration_seconds  = Column(Float, nullable=True)
    prompt_tokens     = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens      = Column(Integer, nullable=True)
    estimated_cost_usd= Column(Float, nullable=True)

    status = Column(String, default="pending")         # pending | running | completed | failed
    error  = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
