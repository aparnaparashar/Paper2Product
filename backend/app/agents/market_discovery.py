import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent
from app.core.config import get_settings

settings = get_settings()

PROMPT = ChatPromptTemplate.from_template("""
You are a market research expert. Identify all viable commercial markets.

Research Profile: {research_profile}
Technical Assessment: {innovation_score}
Live Web Context: {search_results}

Return ONLY valid JSON:
{{
  "primary_market": {{
    "name": "Healthcare AI",
    "size_usd_billion": 45.2,
    "growth_rate_pct": 44.0,
    "description": "AI-powered diagnostic and clinical decision support tools"
  }},
  "adjacent_markets": [
    {{"name": "Medical Imaging", "size_usd_billion": 12.0, "relevance": "direct application"}}
  ],
  "top_industries": ["Healthcare", "Pharmaceuticals", "MedTech"],
  "geographic_opportunity": "global|north-america|europe|asia-pacific|emerging-markets",
  "market_timing": "too-early|ideal|mature|late",
  "demand_signals": ["signal 1", "signal 2"],
  "pain_points_solved": ["pain 1", "pain 2"],
  "use_cases": [
    {{"title": "use case", "description": "how it solves a real problem", "urgency": "high|medium|low"}}
  ],
  "market_verdict": "1-2 sentence opportunity summary",
  "reasoning": [
    "Healthcare selected as primary market because domain is medical imaging and $45B market",
    "Timing rated ideal — post-COVID telehealth adoption accelerated AI diagnostic demand",
    "Adjacent market Medical Imaging included because research directly applies to scan analysis"
  ],
  "confidence": 0.79,
  "sources": [
    "Web search: healthcare AI market report 2024",
    "Research profile — domain field: medical imaging",
    "Technical assessment — technical_readiness field"
  ]
}}
""")


def _web_search(query: str) -> str:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.tavily_api_key)
        results = client.search(query, max_results=5)
        snippets = [r.get("content", "")[:300] for r in results.get("results", [])]
        return "\n\n".join(snippets)
    except Exception:
        return "Web search unavailable — using training knowledge."


def market_discovery_node(state: ResearchState) -> ResearchState:
    profile = state["research_profile"] or {}
    query = f"{profile.get('domain', 'technology')} market size commercial applications {profile.get('problem', '')[:80]}"
    search_results = _web_search(query)

    provider, model = MODEL_ROUTING["market_discovery"]
    output, meta = run_agent(
        "market_discovery", provider, model, PROMPT,
        {
            "research_profile": json.dumps(profile, indent=2),
            "innovation_score": json.dumps(state["innovation_score"], indent=2),
            "search_results": search_results,
        },
        state["project_id"], temperature=0.3,
    )
    state["market_opportunities"] = output
    state.setdefault("agent_metadata", {})["market_discovery"] = meta
    return state
