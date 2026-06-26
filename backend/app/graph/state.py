from typing import TypedDict, Optional


class ResearchState(TypedDict):
    project_id: str
    raw_text: str

    research_profile:      Optional[dict]
    innovation_score:      Optional[dict]
    market_opportunities:  Optional[dict]
    customer_personas:     Optional[list]
    competitive_landscape: Optional[dict]
    product_concepts:      Optional[list]
    mvp_plan:              Optional[dict]
    architecture:          Optional[dict]
    revenue_strategy:      Optional[dict]   # NOTE: matches DB field, NOT node name
    risk_profile:          Optional[dict]
    investment_score:      Optional[dict]
    knowledge_graph:       Optional[dict]
    opportunity_scores:    Optional[dict]
    debate_transcript:     Optional[list]
    final_report:          Optional[dict]

    agent_metadata: Optional[dict]
    awaiting_hitl:  Optional[str]
    hitl_approved:  Optional[bool]
    hitl_feedback:  Optional[str]
    error:          Optional[str]


# Progress steps shown in the UI — now 8 stages instead of 15 sequential
AGENT_STEPS = [
    ("research_analyst",   "Research Analyst",                          7),
    ("stage2",             "Technical Validator + Market Discovery",    21),
    ("stage3",             "Personas + Competitors + Knowledge Graph",  35),
    ("stage4",             "Product Strategy + Risk + Investment",      56),
    ("stage5",             "MVP + Architecture + Revenue",              70),
    ("opportunity_scorer", "Opportunity Scorer",                        82),
    ("debate",             "Agent Debate",                              93),
    ("judge",              "Judge Agent",                              100),
]

# ── Model routing — all Groq, alternating models to stay under RPM cap ────────
MODEL_ROUTING = {
    "research_analyst":    ("groq", "llama-3.3-70b-versatile"),
    "technical_validator": ("groq", "llama-3.1-8b-instant"),
    "market_discovery":    ("groq", "llama-3.3-70b-versatile"),
    "customer_persona":    ("groq", "llama-3.1-8b-instant"),
    "competitor_intel":    ("groq", "llama-3.3-70b-versatile"),
    "knowledge_graph":     ("groq", "llama-3.1-8b-instant"),
    "product_strategist":  ("groq", "llama-3.3-70b-versatile"),
    "risk_analyst":        ("groq", "llama-3.1-8b-instant"),
    "investment_agent":    ("groq", "llama-3.3-70b-versatile"),
    "mvp_planner":         ("groq", "llama-3.1-8b-instant"),
    "architect":           ("groq", "llama-3.1-8b-instant"),
    "revenue_strategy":    ("groq", "llama-3.3-70b-versatile"),
    "opportunity_scorer":  ("groq", "llama-3.3-70b-versatile"),
    "debate":              ("groq", "llama-3.1-8b-instant"),
    "judge":               ("groq", "llama-3.3-70b-versatile"),
}

# DB field each individual agent writes to (used inside agents, not workflow nodes)
FIELD_MAP = {
    "research_analyst":    "research_profile",
    "technical_validator": "innovation_score",
    "market_discovery":    "market_opportunities",
    "customer_persona":    "customer_personas",
    "competitor_intel":    "competitive_landscape",
    "product_strategist":  "product_concepts",
    "mvp_planner":         "mvp_plan",
    "architect":           "architecture",
    "revenue_strategy":    "revenue_strategy",
    "risk_analyst":        "risk_profile",
    "investment_agent":    "investment_score",
    "knowledge_graph":     "knowledge_graph",
    "opportunity_scorer":  "opportunity_scores",
    "debate":              "debate_transcript",
    "judge":               "final_report",
}

PRICING = {
    "llama-3.3-70b-versatile": (0.00059, 0.00079),
    "llama-3.1-8b-instant":    (0.00005, 0.00008),
}