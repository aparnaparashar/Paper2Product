import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a customer research expert. Define 3 distinct customer personas who would pay for a product built on this research.

Research: {research_profile}
Market: {market_opportunities}

Return ONLY valid JSON:
{{
  "personas": [
    {{
      "name": "The Enterprise CTO",
      "type": "B2B",
      "role": "Chief Technology Officer",
      "company_size": "enterprise",
      "industry": "Healthcare",
      "pain_points": ["specific pain 1", "specific pain 2"],
      "goals": ["goal 1"],
      "willingness_to_pay": "high",
      "budget_range": "$2000-$5000/month",
      "decision_process": "6-month procurement cycle with pilot",
      "channels": ["LinkedIn", "Industry conferences"],
      "quote": "A realistic quote describing their problem",
      "priority": "primary"
    }}
  ],
  "reasoning": [
    "Enterprise CTO selected as primary because market shows B2B dominance in healthcare",
    "Budget range derived from comparable SaaS tools in the medical AI space",
    "B2C excluded because regulatory barriers prevent direct-to-consumer medical AI"
  ],
  "confidence": 0.81,
  "sources": [
    "Market opportunities — primary_market: healthcare enterprise segment",
    "Market opportunities — use_cases: B2B urgency signals"
  ]
}}
""")


def customer_persona_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["customer_persona"]
    output, meta = run_agent(
        "customer_persona", provider, model, PROMPT,
        {
            "research_profile": json.dumps(state["research_profile"], indent=2),
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
        },
        state["project_id"], temperature=0.4,
    )
    # Unwrap personas array if nested
    personas = output.get("personas", output) if isinstance(output, dict) else output
    state["customer_personas"] = personas if isinstance(personas, list) else [personas]
    state.setdefault("agent_metadata", {})["customer_persona"] = meta
    return state
