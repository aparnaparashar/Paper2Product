import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are the chief judge of an AI venture studio. You have all 11 specialist agent outputs
PLUS a structured debate transcript where 4 agents argued different positions.

Resolve every conflict in the debate and produce the final definitive verdict.

--- ALL AGENT OUTPUTS ---
Research: {research_profile}
Technical: {innovation_score}
Market: {market_opportunities}
Customers: {customer_personas}
Competition: {competitive_landscape}
Product: {product_concepts}
MVP: {mvp_plan}
Architecture: {architecture}
Revenue: {revenue_strategy}
Risk: {risk_profile}
Investment: {investment_score}
Opportunity Scores: {opportunity_scores}
Knowledge Graph: {knowledge_graph}

--- DEBATE TRANSCRIPT ---
{debate_transcript}

Return ONLY valid JSON:
{{
  "executive_summary": "4-5 sentence summary of the entire opportunity",
  "overall_verdict": "not-viable|needs-validation|promising|strong-opportunity|exceptional",
  "confidence_level": "low|medium|high",
  "recommended_action": "concrete next step the founder should take this week",

  "debate_resolution": [
    {{
      "conflict": "what the agents disagreed on",
      "product_argument": "what Product Agent said",
      "risk_argument": "what Risk Agent said",
      "judge_ruling": "final decision",
      "ruling_rationale": "why this ruling"
    }}
  ],

  "top_product_recommendation": {{
    "name": "product name",
    "why": "why this is the best bet",
    "first_3_steps": ["step 1", "step 2", "step 3"]
  }},

  "headline_metrics": {{
    "market_size_usd_billion": 45.2,
    "final_opportunity_score": 7.6,
    "investment_score": 74,
    "mvp_time_weeks": 10,
    "risk_level": "medium"
  }},

  "go_no_go": "GO|NO-GO|CONDITIONAL-GO",
  "conditions_if_conditional": ["condition to satisfy before proceeding"],

  "final_recommendation_paragraphs": [
    "Paragraph 1: opportunity overview and why it matters",
    "Paragraph 2: recommended product strategy and target market",
    "Paragraph 3: key risks and how to mitigate them",
    "Paragraph 4: funding path and immediate next steps"
  ],

  "reasoning": [
    "GO verdict because opportunity score 7.6 exceeds median threshold 5.5",
    "Debate resolved in favour of Product Agent on market size — Risk Agent regulatory concern addressed by non-FDA entry point",
    "Investment Agent revenue skepticism partially valid — projections adjusted to conservative case in recommendation"
  ],
  "confidence": 0.86,
  "sources": [
    "Opportunity scores — weighted_final_score 7.6, 72nd percentile",
    "Debate transcript — Product vs Risk conflict on regulatory barriers",
    "Investment score — funding_path milestones"
  ]
}}
""")


def judge_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["judge"]
    output, meta = run_agent(
        "judge", provider, model, PROMPT,
        {
            "research_profile":      json.dumps(state["research_profile"], indent=2),
            "innovation_score":      json.dumps(state["innovation_score"], indent=2),
            "market_opportunities":  json.dumps(state["market_opportunities"], indent=2),
            "customer_personas":     json.dumps(state["customer_personas"], indent=2),
            "competitive_landscape": json.dumps(state["competitive_landscape"], indent=2),
            "product_concepts":      json.dumps(state["product_concepts"], indent=2),
            "mvp_plan":              json.dumps(state["mvp_plan"], indent=2),
            "architecture":          json.dumps(state["architecture"], indent=2),
            "revenue_strategy":      json.dumps(state["revenue_strategy"], indent=2),
            "risk_profile":          json.dumps(state["risk_profile"], indent=2),
            "investment_score":      json.dumps(state["investment_score"], indent=2),
            "opportunity_scores":    json.dumps(state.get("opportunity_scores"), indent=2),
            "knowledge_graph":       json.dumps(state.get("knowledge_graph"), indent=2),
            "debate_transcript":     json.dumps(state.get("debate_transcript"), indent=2),
        },
        state["project_id"], temperature=0.2,
    )
    state["final_report"] = output
    state.setdefault("agent_metadata", {})["judge"] = meta
    return state
