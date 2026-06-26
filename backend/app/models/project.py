import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Float
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String, nullable=False, default="Untitled Project")
    status = Column(String, default="pending")
    # pending | processing | awaiting_hitl | completed | failed
    current_agent = Column(String, nullable=True)
    progress = Column(String, default="0")

    # Human-in-the-loop pause point
    hitl_pending_agent = Column(String, nullable=True)
    hitl_pending_data = Column(JSON, nullable=True)

    # Raw input
    file_name = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)

    # ── Agent outputs ──────────────────────────────────────────
    research_profile     = Column(JSON, nullable=True)
    innovation_score     = Column(JSON, nullable=True)
    market_opportunities = Column(JSON, nullable=True)
    customer_personas    = Column(JSON, nullable=True)
    competitive_landscape= Column(JSON, nullable=True)
    product_concepts     = Column(JSON, nullable=True)
    mvp_plan             = Column(JSON, nullable=True)
    architecture         = Column(JSON, nullable=True)
    revenue_strategy     = Column(JSON, nullable=True)
    risk_profile         = Column(JSON, nullable=True)
    investment_score     = Column(JSON, nullable=True)

    # New feature outputs
    knowledge_graph      = Column(JSON, nullable=True)   # Feature 10
    opportunity_scores   = Column(JSON, nullable=True)   # Feature 3
    debate_transcript    = Column(JSON, nullable=True)   # Feature 2
    final_report         = Column(JSON, nullable=True)

    # Aggregate evaluation metrics (Feature 9)
    total_tokens         = Column(JSON, nullable=True)   # {total: N}
    total_cost_usd       = Column(Float, nullable=True)
    total_duration_sec   = Column(Float, nullable=True)

    error_message = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at  = Column(DateTime, nullable=True)
