import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a venture scoring specialist. Produce a rigorous multi-dimensional opportunity score.

Score each dimension 1.0–10.0 with specific justification.

Innovation: {innovation_score}
Market: {market_opportunities}
Competition: {competitive_landscape}
MVP: {mvp_plan}
Revenue: {revenue_strategy}
Risk: {risk_profile}
Investment: {investment_score}

Return ONLY valid JSON:
{{
  "dimensions": {{
    "technical_feasibility": {{
      "score": 8.2,
      "weight": 0.20,
      "rationale": "Prototype stage, dependencies are mature, team can reproduce results"
    }},
    "market_opportunity": {{
      "score": 7.9,
      "weight": 0.25,
      "rationale": "$45B market, 44% CAGR, ideal timing, 3 high-urgency use cases"
    }},
    "competitive_advantage": {{
      "score": 6.4,
      "weight": 0.15,
      "rationale": "Moat moderate — 2 direct competitors but clear whitespace in SMB"
    }},
    "execution_difficulty": {{
      "score": 7.0,
      "weight": 0.15,
      "rationale": "High build complexity but standard ML stack, 8-12 week MVP achievable"
    }},
    "revenue_potential": {{
      "score": 8.7,
      "weight": 0.15,
      "rationale": "LTV/CAC 6x, SaaS with expansion revenue, Year 3 ARR $2.4M projected"
    }},
    "risk_adjusted_return": {{
      "score": 6.8,
      "weight": 0.10,
      "rationale": "Medium-high risk, but top 3 risks all have clear mitigations"
    }}
  }},
  "weighted_final_score": 7.6,
  "score_interpretation": "Strong opportunity with manageable risks — recommended for MVP investment",
  "score_vs_benchmarks": {{
    "top_10pct_threshold": 8.5,
    "median_startup": 5.5,
    "this_opportunity": 7.6,
    "percentile": 72
  }},
  "improvement_levers": [
    "File provisional patent to raise competitive_advantage from 6.4 to 7.2",
    "Partner with ML infrastructure provider to reduce execution_difficulty from 7.0 to 7.8"
  ],
  "reasoning": [
    "Technical feasibility 8.2 because innovation_score=8 and reproducibility confirmed",
    "Revenue potential rated highest (8.7) due to strong LTV/CAC and expansion revenue paths",
    "Competitive advantage weakest (6.4) — no IP protection currently"
  ],
  "confidence": 0.84,
  "sources": [
    "Innovation score — innovation_score and technical_readiness fields",
    "Market opportunities — primary_market size and growth_rate_pct",
    "Revenue strategy — unit_economics LTV/CAC ratio"
  ]
}}
""")


def opportunity_scorer_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["opportunity_scorer"]
    output, meta = run_agent(
        "opportunity_scorer", provider, model, PROMPT,
        {
            "innovation_score":      json.dumps(state["innovation_score"], indent=2),
            "market_opportunities":  json.dumps(state["market_opportunities"], indent=2),
            "competitive_landscape": json.dumps(state["competitive_landscape"], indent=2),
            "mvp_plan":              json.dumps(state["mvp_plan"], indent=2),
            "revenue_strategy":      json.dumps(state["revenue_strategy"], indent=2),
            "risk_profile":          json.dumps(state["risk_profile"], indent=2),
            "investment_score":      json.dumps(state["investment_score"], indent=2),
        },
        state["project_id"], temperature=0.2,
    )
    state["opportunity_scores"] = output
    state.setdefault("agent_metadata", {})["opportunity_scorer"] = meta
    return state
