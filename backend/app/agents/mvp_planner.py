import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a lean startup expert. Define the smallest product that validates this opportunity.

Primary Product: {primary_product}
Research: {research_profile}
Primary Persona: {primary_persona}

Return ONLY valid JSON:
{{
  "mvp_name": "ClearDiag Lite",
  "mvp_description": "2-sentence description of what the MVP does and for whom",
  "must_have_features": [
    {{"feature": "name", "why": "why essential to test core hypothesis", "effort": "low|medium|high"}}
  ],
  "nice_to_have": ["feature to defer to v2"],
  "explicitly_exclude": ["things NOT to build in MVP — explain why"],
  "validation_goals": ["hypothesis each feature tests"],
  "success_metrics": [
    {{"metric": "weekly active radiologists", "target": "50", "timeframe": "90 days"}}
  ],
  "validation_experiments": [
    {{"experiment": "landing page smoke test", "method": "run Google ads to waitlist signup", "cost": "$500"}}
  ],
  "time_to_mvp": "8-12 weeks",
  "team_needed": ["Full-stack engineer", "ML engineer", "Product designer"],
  "estimated_cost_usd": {{"min": 15000, "max": 40000}},
  "mvp_risks": ["risk that could invalidate the whole approach"],
  "reasoning": [
    "Excluded advanced reporting because it doesn't test core value hypothesis",
    "Time estimate 8-12 weeks based on 3 medium-effort features",
    "Cost range derived from team size × sprint cost"
  ],
  "confidence": 0.80,
  "sources": [
    "Primary product concept — core_value_proposition",
    "Primary persona — pain_points and budget_range"
  ]
}}
""")


def mvp_planner_node(state: ResearchState) -> ResearchState:
    concepts = state["product_concepts"] or []
    primary = concepts[0] if concepts else {}
    personas = state["customer_personas"] or []
    primary_persona = next((p for p in personas if p.get("priority") == "primary"), personas[0] if personas else {})

    provider, model = MODEL_ROUTING["mvp_planner"]
    output, meta = run_agent(
        "mvp_planner", provider, model, PROMPT,
        {
            "primary_product": json.dumps(primary, indent=2),
            "research_profile": json.dumps(state["research_profile"], indent=2),
            "primary_persona": json.dumps(primary_persona, indent=2),
        },
        state["project_id"], temperature=0.3,
    )
    state["mvp_plan"] = output
    state.setdefault("agent_metadata", {})["mvp_planner"] = meta
    return state
