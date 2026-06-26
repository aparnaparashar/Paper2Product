import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState, MODEL_ROUTING
from app.agents.llm_helpers import run_agent

PROMPT = ChatPromptTemplate.from_template("""
You are a CTO-level technical reviewer. Assess the technical validity and innovation.

Research Profile:
{research_profile}

Return ONLY valid JSON:
{{
  "innovation_score": 8,
  "innovation_level": "incremental|significant|breakthrough|paradigm-shift",
  "is_reproducible": true,
  "reproducibility_notes": "why reproducible or not",
  "technical_readiness": 6,
  "dependencies": ["external dependency 1"],
  "technical_risks": ["risk 1", "risk 2"],
  "build_complexity": "low|medium|high|very-high",
  "estimated_engineering_effort": "e.g. 3-6 months, 4-person team",
  "verdict": "1-2 sentence technical verdict",
  "reasoning": [
    "Innovation score 8 because the approach is novel but builds on proven ML techniques",
    "Reproducibility confirmed — paper includes full dataset and code links",
    "Build complexity high due to real-time inference requirements"
  ],
  "confidence": 0.82,
  "sources": [
    "Research profile — methodology and key_technologies fields",
    "Research profile — limitations list",
    "Research profile — maturity_level field"
  ]
}}
""")


def technical_validator_node(state: ResearchState) -> ResearchState:
    provider, model = MODEL_ROUTING["technical_validator"]
    output, meta = run_agent(
        "technical_validator", provider, model, PROMPT,
        {"research_profile": json.dumps(state["research_profile"], indent=2)},
        state["project_id"], temperature=0.2,
    )
    state["innovation_score"] = output
    state.setdefault("agent_metadata", {})["technical_validator"] = meta
    return state
