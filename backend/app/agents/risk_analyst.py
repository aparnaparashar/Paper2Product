import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a risk analyst specialising in deep tech startups. Identify all material risks.

Research: {research_profile}
Technical: {innovation_score}
Market: {market_opportunities}
MVP: {mvp_plan}

Return ONLY valid JSON:
{{
  "overall_risk_level": "low|medium|high|very-high",
  "technical_risks": [
    {{"risk": "description", "likelihood": "high", "impact": "high", "mitigation": "specific action"}}
  ],
  "market_risks": [
    {{"risk": "description", "likelihood": "medium", "impact": "high", "mitigation": "specific action"}}
  ],
  "regulatory_risks": [
    {{"risk": "description", "jurisdiction": "US/EU", "timeline": "when it bites", "mitigation": "action"}}
  ],
  "adoption_risks": [
    {{"risk": "description", "likelihood": "medium", "mitigation": "action"}}
  ],
  "competitive_risks": [
    {{"risk": "description", "threat_source": "who", "mitigation": "action"}}
  ],
  "financial_risks": [
    {{"risk": "description", "mitigation": "action"}}
  ],
  "top_3_risks": ["most critical risk 1", "risk 2", "risk 3"],
  "risk_verdict": "1-2 sentence overall risk assessment",
  "reasoning": [
    "Overall rated high because FDA clearance is required and adds 18-month delay",
    "Technical risk #1 rated high because ML drift is common in medical imaging without retraining",
    "Market adoption risk reduced because demand signals exist in web search results"
  ],
  "confidence": 0.85,
  "sources": [
    "Innovation score — technical_risks list",
    "Market opportunities — market_timing field",
    "Research profile — limitations list"
  ]
}}
""")


def risk_analyst_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["risk_analyst"]
    output, meta = run_agent(
        "risk_analyst", provider, model, PROMPT,
        {
            "research_profile": json.dumps(state["research_profile"], indent=2),
            "innovation_score": json.dumps(state["innovation_score"], indent=2),
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
            "mvp_plan": json.dumps(state["mvp_plan"], indent=2),
        },
        state["project_id"], temperature=0.2,
    )
    state["risk_profile"] = output
    state.setdefault("agent_metadata", {})["risk_analyst"] = meta
    return state
