import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a world-class product strategist. Generate 2-3 concrete product concepts from this research.

Research: {research_profile}
Market: {market_opportunities}
Customers: {customer_personas}
Competition: {competitive_landscape}

Return ONLY valid JSON:
{{
  "concepts": [
    {{
      "product_name": "ClearDiag",
      "tagline": "AI-powered diagnostic support for radiologists",
      "category": "SaaS|API|Platform|Marketplace|Mobile App|Desktop",
      "target_persona": "which persona",
      "core_value_proposition": "unique value delivered",
      "key_features": [{{"feature": "name", "why": "why it matters"}}],
      "user_journey": ["step 1: user does X", "step 2: product does Y", "outcome: user gets Z"],
      "positioning": "how to position vs competitors",
      "go_to_market": "initial GTM strategy",
      "priority": "primary|secondary|tertiary"
    }}
  ],
  "reasoning": [
    "SaaS chosen over API because personas are non-technical healthcare buyers",
    "Healthcare vertical prioritised — largest market at $45B with high urgency",
    "Feature set derived from primary persona's top 2 pain points"
  ],
  "confidence": 0.83,
  "sources": [
    "Customer personas — primary persona pain_points",
    "Competitive landscape — whitespace_opportunities",
    "Market opportunities — use_cases urgency signals"
  ]
}}
""")


def product_strategist_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["product_strategist"]
    output, meta = run_agent(
        "product_strategist", provider, model, PROMPT,
        {
            "research_profile": json.dumps(state["research_profile"], indent=2),
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
            "customer_personas": json.dumps(state["customer_personas"], indent=2),
            "competitive_landscape": json.dumps(state["competitive_landscape"], indent=2),
        },
        state["project_id"], temperature=0.5,
    )
    concepts = output.get("concepts", []) if isinstance(output, dict) else output
    state["product_concepts"] = concepts if isinstance(concepts, list) else [concepts]
    state.setdefault("agent_metadata", {})["product_strategist"] = meta
    return state
