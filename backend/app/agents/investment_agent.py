import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a Tier-1 VC analyst preparing an investment memo. Be rigorous and data-driven.

Market: {market_opportunities}
Technical: {innovation_score}
Revenue: {revenue_strategy}
Risk: {risk_profile}
Competition: {competitive_landscape}

Return ONLY valid JSON:
{{
  "investment_score": 74,
  "investment_verdict": "pass|watch|invest|strong-invest",
  "scores": {{
    "market_attractiveness": 8,
    "technical_defensibility": 7,
    "team_requirement": 6,
    "scalability": 8,
    "monetisation": 7,
    "timing": 8
  }},
  "comparable_companies": [
    {{"company": "Veeva Systems", "outcome": "IPO $2.4B", "valuation": "$2.4B",
      "relevance": "vertical SaaS in regulated healthcare industry"}}
  ],
  "funding_path": {{
    "pre_seed": {{"amount_usd": 500000, "use_of_funds": ["build MVP", "first 5 paying customers"]}},
    "seed": {{"amount_usd": 2000000, "milestones": ["$50K MRR", "3 enterprise pilots"]}},
    "series_a": {{"amount_usd": 10000000, "metrics_needed": ["$1M ARR", "NPS > 50", "3 case studies"]}}
  }},
  "investor_types": ["Healthcare-focused VCs", "Corporate VCs from hospital groups"],
  "bull_case": "best case scenario in 5 years if everything goes right",
  "bear_case": "realistic worst case in 5 years",
  "key_milestones": ["milestone before pre-seed", "milestone before seed", "milestone before Series A"],
  "investment_memo_summary": "3-4 sentence VC-style investment thesis",
  "reasoning": [
    "Investment score 74 driven by strong market_attractiveness (8) and timing (8)",
    "Technical defensibility rated 7 — moat exists but takes 18 months to build",
    "Comparable to Veeva early stage: vertical SaaS in regulated industry with high switching costs"
  ],
  "confidence": 0.80,
  "sources": [
    "Market opportunities — primary_market size and growth_rate",
    "Revenue strategy — unit_economics LTV/CAC ratio",
    "Risk profile — overall_risk_level and top_3_risks"
  ]
}}
""")


def investment_agent_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["investment_agent"]
    output, meta = run_agent(
        "investment_agent", provider, model, PROMPT,
        {
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
            "innovation_score": json.dumps(state["innovation_score"], indent=2),
            "revenue_strategy": json.dumps(state["revenue_strategy"], indent=2),
            "risk_profile": json.dumps(state["risk_profile"], indent=2),
            "competitive_landscape": json.dumps(state["competitive_landscape"], indent=2),
        },
        state["project_id"], temperature=0.3,
    )
    state["investment_score"] = output
    state.setdefault("agent_metadata", {})["investment_agent"] = meta
    return state
