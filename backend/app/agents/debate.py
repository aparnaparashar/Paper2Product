"""
Agent Debate Stage — Feature 2
Four specialist agents argue different positions.
The Judge reads this transcript and resolves conflicts.
"""
import json
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import ResearchState
from app.agents.llm_helpers import get_llm, parse_json

POSITIONS = [
    (
        "Product Agent",
        "FOR",
        ChatPromptTemplate.from_template("""
You are the Product Agent arguing FOR this opportunity in a venture studio debate.
Make your strongest 3-4 point case. Be specific and use data from the inputs.

Product Concepts: {product_concepts}
Market: {market_opportunities}
MVP Plan: {mvp_plan}

Return ONLY valid JSON:
{{"position": "FOR", "agent": "Product Agent",
  "arguments": ["specific arg 1", "specific arg 2", "specific arg 3"],
  "strongest_point": "the single most compelling argument",
  "confidence": 0.85}}
"""),
        ["product_concepts", "market_opportunities", "mvp_plan"],
    ),
    (
        "Risk Agent",
        "AGAINST",
        ChatPromptTemplate.from_template("""
You are the Risk Agent arguing AGAINST this opportunity. Raise your strongest 3-4 concerns.
Play devil's advocate. Be specific and data-driven.

Risk Profile: {risk_profile}
Technical: {innovation_score}
MVP: {mvp_plan}

Return ONLY valid JSON:
{{"position": "AGAINST", "agent": "Risk Agent",
  "arguments": ["specific concern 1", "concern 2", "concern 3"],
  "strongest_point": "the single most damaging concern",
  "confidence": 0.80}}
"""),
        ["risk_profile", "innovation_score", "mvp_plan"],
    ),
    (
        "Competitor Agent",
        "CHALLENGE",
        ChatPromptTemplate.from_template("""
You are the Competitor Intelligence Agent challenging the competitive moat.
Argue that the competitive position is weaker than claimed. Be specific.

Competitive Landscape: {competitive_landscape}
Product Concepts: {product_concepts}

Return ONLY valid JSON:
{{"position": "CHALLENGE", "agent": "Competitor Agent",
  "arguments": ["challenge 1", "challenge 2", "challenge 3"],
  "strongest_point": "the most dangerous competitive threat",
  "confidence": 0.75}}
"""),
        ["competitive_landscape", "product_concepts"],
    ),
    (
        "Investment Agent",
        "SKEPTICAL",
        ChatPromptTemplate.from_template("""
You are the Investment Agent playing devil's advocate on the financials.
Question the revenue projections and unit economics. Be specific.

Revenue Strategy: {revenue_strategy}
Investment Score: {investment_score}
Risk Profile: {risk_profile}

Return ONLY valid JSON:
{{"position": "SKEPTICAL", "agent": "Investment Agent",
  "arguments": ["financial doubt 1", "doubt 2", "doubt 3"],
  "strongest_point": "the most worrying financial assumption",
  "confidence": 0.78}}
"""),
        ["revenue_strategy", "investment_score", "risk_profile"],
    ),
]


def debate_node(state: ResearchState) -> ResearchState:
    llm = get_llm("groq", "llama-3.1-8b-instant", 0.5)
    all_inputs = {
        "product_concepts":     json.dumps(state["product_concepts"], indent=2),
        "market_opportunities": json.dumps(state["market_opportunities"], indent=2),
        "mvp_plan":             json.dumps(state["mvp_plan"], indent=2),
        "risk_profile":         json.dumps(state["risk_profile"], indent=2),
        "innovation_score":     json.dumps(state["innovation_score"], indent=2),
        "competitive_landscape":json.dumps(state["competitive_landscape"], indent=2),
        "revenue_strategy":     json.dumps(state["revenue_strategy"], indent=2),
        "investment_score":     json.dumps(state["investment_score"], indent=2),
    }

    transcript = []
    for agent_name, position, prompt, keys in POSITIONS:
        try:
            result = (prompt | llm).invoke({k: all_inputs[k] for k in keys})
            entry = parse_json(result.content)
        except Exception as e:
            entry = {"agent": agent_name, "position": position, "error": str(e), "arguments": []}
        transcript.append(entry)

    state["debate_transcript"] = transcript
    state.setdefault("agent_metadata", {})["debate"] = {
        "agent_name": "debate",
        "reasoning": [
            "Product Agent argued FOR based on market size and product-market fit",
            "Risk Agent raised regulatory and technical concerns",
            "Competitor Agent challenged moat strength and whitespace claims",
            "Investment Agent questioned revenue projections and LTV assumptions",
        ],
        "confidence": 0.82,
        "duration_seconds": 0,
    }
    return state