from pydantic import BaseModel, EmailStr
from typing import Optional, Any, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str; email: str; full_name: Optional[str]; created_at: datetime
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str; token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr; password: str


class ProjectStatusResponse(BaseModel):
    id: str; title: str; status: str
    current_agent: Optional[str]; progress: str
    error_message: Optional[str]
    hitl_pending_agent: Optional[str]; hitl_pending_data: Optional[Any]
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True

class ProjectReportResponse(BaseModel):
    id: str; title: str; status: str; file_name: Optional[str]
    research_profile: Optional[Any]; innovation_score: Optional[Any]
    market_opportunities: Optional[Any]; customer_personas: Optional[Any]
    competitive_landscape: Optional[Any]; product_concepts: Optional[Any]
    mvp_plan: Optional[Any]; architecture: Optional[Any]
    revenue_strategy: Optional[Any]; risk_profile: Optional[Any]
    investment_score: Optional[Any]; opportunity_scores: Optional[Any]
    knowledge_graph: Optional[Any]; debate_transcript: Optional[Any]
    final_report: Optional[Any]
    total_tokens: Optional[Any]; total_cost_usd: Optional[float]
    total_duration_sec: Optional[float]
    created_at: datetime; completed_at: Optional[datetime]
    class Config: from_attributes = True

class ProjectListItem(BaseModel):
    id: str; title: str; status: str; progress: str
    file_name: Optional[str]; total_cost_usd: Optional[float]
    created_at: datetime
    class Config: from_attributes = True

class AgentRunResponse(BaseModel):
    id: str; project_id: str; agent_name: str; agent_label: Optional[str]
    model_used: Optional[str]; model_provider: Optional[str]
    output: Optional[Any]; reasoning: Optional[Any]; confidence: Optional[float]
    sources: Optional[Any]; duration_seconds: Optional[float]
    prompt_tokens: Optional[int]; completion_tokens: Optional[int]
    total_tokens: Optional[int]; estimated_cost_usd: Optional[float]
    status: str; error: Optional[str]; created_at: datetime
    class Config: from_attributes = True

class HITLDecision(BaseModel):
    approved: bool; feedback: Optional[str] = None
