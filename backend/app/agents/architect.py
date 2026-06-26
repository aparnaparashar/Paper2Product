import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a principal software architect. Design the MVP technical architecture.

MVP Plan: {mvp_plan}
Product: {primary_product}
Research: {research_profile}

Return ONLY valid JSON:
{{
  "architecture_type": "monolith|microservices|serverless|hybrid",
  "backend": {{"language": "Python", "framework": "FastAPI", "rationale": "why this stack"}},
  "frontend": {{"framework": "React", "ui_library": "Tailwind + shadcn", "deployment": "Vercel"}},
  "ai_ml_stack": {{
    "model_providers": ["Google Gemini 2.5 Flash", "Groq"],
    "frameworks": ["LangChain", "LangGraph"],
    "serving": "API calls — no self-hosting needed for MVP",
    "fine_tuning_needed": false
  }},
  "data_storage": [
    {{"type": "PostgreSQL", "purpose": "users, projects, reports", "reason": "relational data, ACID compliance"}}
  ],
  "infrastructure": {{
    "cloud": "AWS|GCP|Azure",
    "key_services": ["EC2 or Render", "S3", "CloudFront"],
    "estimated_monthly_cost_usd": {{"mvp": 150, "scale_10k_users": 1800}}
  }},
  "integrations": ["third-party APIs needed"],
  "security_considerations": ["JWT auth", "HTTPS only", "data encryption at rest"],
  "scalability_path": "how to scale from 100 to 10,000 users",
  "tech_debt_risks": ["shortcuts in MVP that need addressing before scale"],
  "reasoning": [
    "FastAPI chosen for Python ML ecosystem compatibility and async support",
    "PostgreSQL over MongoDB because data is relational",
    "Serverless rejected due to cold-start latency with ML model calls"
  ],
  "confidence": 0.88,
  "sources": [
    "MVP plan — must_have_features informed stack selection",
    "Research profile — key_technologies list",
    "Product concept — category field"
  ]
}}
""")


def architect_node(state: ResearchState) -> ResearchState:
    concepts = state["product_concepts"] or []
    primary = concepts[0] if concepts else {}

    provider, model = MODEL_ROUTING["architect"]
    output, meta = run_agent(
        "architect", provider, model, PROMPT,
        {
            "mvp_plan": json.dumps(state["mvp_plan"], indent=2),
            "primary_product": json.dumps(primary, indent=2),
            "research_profile": json.dumps(state["research_profile"], indent=2),
        },
        state["project_id"], temperature=0.2,
    )
    state["architecture"] = output
    state.setdefault("agent_metadata", {})["architect"] = meta
    return state
