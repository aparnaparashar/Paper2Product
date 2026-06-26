import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent
from app.core.config import get_settings

settings = get_settings()

PROMPT = ChatPromptTemplate.from_template("""
You are a competitive intelligence analyst. Map the full competitive landscape.

Research: {research_profile}
Market: {market_opportunities}
Web Search Results: {search_results}

Return ONLY valid JSON:
{{
  "direct_competitors": [
    {{"name": "Company", "description": "what they do", "funding": "Series B $20M",
      "weakness": "their key gap", "url": "website.com"}}
  ],
  "indirect_competitors": [
    {{"name": "name", "description": "indirect threat", "overlap": "area of overlap"}}
  ],
  "open_source_alternatives": [
    {{"name": "project", "description": "what it does", "limitation": "key limitation"}}
  ],
  "market_saturation": "unsaturated|emerging|competitive|saturated",
  "whitespace_opportunities": ["specific gap 1", "gap 2"],
  "competitive_advantages": ["advantage this research has"],
  "moat_potential": "weak|moderate|strong|very-strong",
  "moat_sources": ["IP", "data network effects", "switching costs"],
  "competitive_verdict": "1-2 sentence positioning summary",
  "reasoning": [
    "Market saturation rated emerging — only 2 direct competitors found via web search",
    "Moat rated strong because proprietary training data creates switching costs",
    "Whitespace in SMB segment: all competitors target enterprise only"
  ],
  "confidence": 0.74,
  "sources": [
    "Web search: competitor names from search results",
    "Market opportunities — market_saturation signals",
    "Research profile — novelty field"
  ]
}}
""")


def _search(query: str) -> str:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.tavily_api_key)
        r = client.search(query, max_results=6)
        return "\n\n".join(x.get("content", "")[:300] for x in r.get("results", []))
    except Exception:
        return "Web search unavailable."


def competitor_intel_node(state: ResearchState) -> ResearchState:
    profile = state["research_profile"] or {}
    query = f"startups companies solving {profile.get('problem', '')[:80]} {profile.get('domain', '')} 2024"
    search_results = _search(query)

    provider, model = MODEL_ROUTING["competitor_intel"]
    output, meta = run_agent(
        "competitor_intel", provider, model, PROMPT,
        {
            "research_profile": json.dumps(profile, indent=2),
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
            "search_results": search_results,
        },
        state["project_id"], temperature=0.3,
    )
    state["competitive_landscape"] = output
    state.setdefault("agent_metadata", {})["competitor_intel"] = meta
    return state
