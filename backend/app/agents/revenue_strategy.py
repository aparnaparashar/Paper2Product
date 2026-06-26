import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a SaaS monetisation expert. Design the revenue strategy.

Product: {primary_product}
Customers: {customer_personas}
Competition: {competitive_landscape}
Market: {market_opportunities}

Return ONLY valid JSON:
{{
  "recommended_model": "SaaS|API|Marketplace|Licensing|Freemium|Usage-based|Enterprise",
  "rationale": "why this model fits best",
  "pricing_tiers": [
    {{"name": "Starter", "price": "$99/month", "target": "which persona",
      "features": ["what's included"], "limits": "usage limits"}}
  ],
  "freemium_strategy": "what is free vs paid, or why no freemium",
  "enterprise_play": "enterprise sales motion",
  "revenue_projections": {{
    "month_6": {{"customers": 50, "mrr_usd": 4950}},
    "year_1": {{"customers": 300, "arr_usd": 356400}},
    "year_3": {{"customers": 2000, "arr_usd": 2376000}}
  }},
  "unit_economics": {{
    "cac_usd": 800, "ltv_usd": 4800, "ltv_cac_ratio": 6.0, "payback_months": 9
  }},
  "expansion_revenue": "how to grow revenue per customer over time",
  "alternative_models": ["other viable models"],
  "revenue_risks": ["churn risk", "pricing sensitivity"],
  "reasoning": [
    "SaaS selected — personas prefer predictable monthly costs over usage-based",
    "LTV/CAC of 6x based on 24-month average retention in comparable healthcare SaaS",
    "Freemium excluded — product requires onboarding investment not suited to self-serve"
  ],
  "confidence": 0.77,
  "sources": [
    "Customer personas — willingness_to_pay and budget_range",
    "Competitive landscape — competitor pricing signals from web search"
  ]
}}
""")


def revenue_strategy_node(state: ResearchState) -> ResearchState:
    concepts = state["product_concepts"] or []
    primary = concepts[0] if concepts else {}

    provider, model = MODEL_ROUTING["revenue_strategy"]
    output, meta = run_agent(
        "revenue_strategy", provider, model, PROMPT,
        {
            "primary_product": json.dumps(primary, indent=2),
            "customer_personas": json.dumps(state["customer_personas"], indent=2),
            "competitive_landscape": json.dumps(state["competitive_landscape"], indent=2),
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
        },
        state["project_id"], temperature=0.3,
    )
    state["revenue_strategy"] = output
    state.setdefault("agent_metadata", {})["revenue_strategy"] = meta
    return state
