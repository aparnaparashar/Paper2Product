import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a knowledge graph specialist. Extract entities and relationships to build a concept map.

Research: {research_profile}
Market: {market_opportunities}
Customers: {customer_personas}
Competition: {competitive_landscape}

Return ONLY valid JSON:
{{
  "entities": [
    {{
      "id": "e1",
      "label": "Crop Disease Detection",
      "type": "technology|market|customer|problem|solution|regulation|competitor",
      "description": "brief description"
    }}
  ],
  "relationships": [
    {{
      "from": "e1",
      "to": "e2",
      "label": "enables",
      "strength": "strong|moderate|weak"
    }}
  ],
  "core_concept": "the central node all others connect to",
  "concept_clusters": [
    {{
      "cluster_name": "Technology Layer",
      "entity_ids": ["e1", "e2"],
      "insight": "what this cluster reveals about the opportunity"
    }}
  ],
  "graph_insight": "What does this knowledge graph reveal about the commercialisation opportunity?",
  "reasoning": [
    "Identified 3 clusters: technology, market, and customer layers",
    "Core concept is the ML model because all other entities depend on it",
    "Regulation entity added because healthcare domain triggers FDA compliance path"
  ],
  "confidence": 0.78,
  "sources": [
    "Research profile — key_technologies and domain",
    "Market opportunities — top_industries",
    "Customer personas — industries and roles"
  ]
}}
""")


def knowledge_graph_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["knowledge_graph"]
    output, meta = run_agent(
        "knowledge_graph", provider, model, PROMPT,
        {
            "research_profile": json.dumps(state["research_profile"], indent=2),
            "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
            "customer_personas": json.dumps(state["customer_personas"], indent=2),
            "competitive_landscape": json.dumps(state["competitive_landscape"], indent=2),
        },
        state["project_id"], temperature=0.3,
    )
    state["knowledge_graph"] = output
    state.setdefault("agent_metadata", {})["knowledge_graph"] = meta
    return state
