from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent, trunc

PROMPT = ChatPromptTemplate.from_template("""
You are an expert research analyst. Extract structured information from this document.

Return ONLY valid JSON:
{{
  "title": "paper title",
  "domain": "primary scientific/technical domain",
  "problem": "core problem being addressed",
  "methodology": "key methods used",
  "results": "main findings",
  "novelty": "what is genuinely new or innovative",
  "limitations": ["limitation 1"],
  "key_technologies": ["tech1", "tech2"],
  "maturity_level": "theoretical|experimental|prototype|validated|production-ready",
  "summary": "2-3 sentence plain-English summary",
  "reasoning": [
    "Domain classified as X because the paper focuses on Y",
    "Novelty rated high because no prior work addresses Z",
    "Maturity set to prototype because experiments were conducted on limited dataset"
  ],
  "confidence": 0.87,
  "sources": [
    "Abstract — problem statement",
    "Section 2 — methodology description",
    "Conclusion — results and claims"
  ]
}}

Document:
{raw_text}
""")


def research_analyst_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["research_analyst"]
    output, meta = run_agent(
        "research_analyst", provider, model, PROMPT,
        {"raw_text": trunc(state["raw_text"], 10000)},
        state["project_id"], temperature=0.2,
    )
    state["research_profile"] = output
    state.setdefault("agent_metadata", {})["research_analyst"] = meta
    return state
