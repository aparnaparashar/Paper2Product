"""
Optimised parallel pipeline — 8 stages instead of 15 sequential steps.
Agents that don't depend on each other run concurrently via ThreadPoolExecutor.

Stage 1 : research_analyst                          (must be first)
Stage 2 : tech_validator || market_discovery        (both need research only)
Stage 3 : customer_persona || competitor_intel || knowledge_graph  (need stage 2)
Stage 4 : product_strategist || risk_analyst || investment_agent   (need stage 3)
Stage 5 : mvp_planner || architect || revenue_strategist           (need stage 4)
Stage 6 : opportunity_scorer                        (needs all scores)
Stage 7 : debate                                    (needs all outputs)
Stage 8 : judge                                     (needs debate + all)

Note: node names must NOT match state keys — fixed by renaming:
  revenue_strategy node  → revenue_strategist
  knowledge_graph node   → knowledge_builder
  investment_agent node  → investment_scorer
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState

from app.agents.research_analyst    import research_analyst_node
from app.agents.technical_validator import technical_validator_node
from app.agents.market_discovery    import market_discovery_node
from app.agents.customer_persona    import customer_persona_node
from app.agents.competitor_intel    import competitor_intel_node
from app.agents.product_strategist  import product_strategist_node
from app.agents.mvp_planner         import mvp_planner_node
from app.agents.architect           import architect_node
from app.agents.revenue_strategy    import revenue_strategy_node
from app.agents.risk_analyst        import risk_analyst_node
from app.agents.investment_agent    import investment_agent_node
from app.agents.knowledge_graph     import knowledge_graph_node
from app.agents.opportunity_scorer  import opportunity_scorer_node
from app.agents.debate              import debate_node
from app.agents.judge               import judge_node


def _run_parallel(state: ResearchState, fns: list) -> ResearchState:
    """Run a list of agent functions concurrently, merging their state updates."""
    with ThreadPoolExecutor(max_workers=len(fns)) as pool:
        futures = {pool.submit(fn, dict(state)): fn for fn in fns}
        for future in as_completed(futures):
            result = future.result()       # raises if agent failed
            state.update(result)           # merge outputs back
            if "agent_metadata" in result and result["agent_metadata"]:
                meta = state.setdefault("agent_metadata", {})
                meta.update(result["agent_metadata"])
    return state


# ── Wrapper nodes (renamed to avoid collision with state keys) ────────────────

def revenue_strategist_node(state):     return revenue_strategy_node(state)
def knowledge_builder_node(state):      return knowledge_graph_node(state)
def investment_scorer_node(state):      return investment_agent_node(state)

# ── Parallel stage nodes ──────────────────────────────────────────────────────

def stage2_node(state: ResearchState) -> ResearchState:
    return _run_parallel(state, [technical_validator_node, market_discovery_node])

def stage3_node(state: ResearchState) -> ResearchState:
    return _run_parallel(state, [customer_persona_node, competitor_intel_node, knowledge_builder_node])

def stage4_node(state: ResearchState) -> ResearchState:
    return _run_parallel(state, [product_strategist_node, risk_analyst_node, investment_scorer_node])

def stage5_node(state: ResearchState) -> ResearchState:
    return _run_parallel(state, [mvp_planner_node, architect_node, revenue_strategist_node])


def build_workflow():
    g = StateGraph(ResearchState)

    g.add_node("research_analyst",  research_analyst_node)
    g.add_node("stage2",            stage2_node)           # tech_validator + market_discovery
    g.add_node("stage3",            stage3_node)           # customer_persona + competitor_intel + knowledge_graph
    g.add_node("stage4",            stage4_node)           # product_strategist + risk_analyst + investment_agent
    g.add_node("stage5",            stage5_node)           # mvp_planner + architect + revenue_strategy
    g.add_node("opportunity_scorer",opportunity_scorer_node)
    g.add_node("debate",            debate_node)
    g.add_node("judge",             judge_node)

    g.set_entry_point("research_analyst")
    g.add_edge("research_analyst",   "stage2")
    g.add_edge("stage2",             "stage3")
    g.add_edge("stage3",             "stage4")
    g.add_edge("stage4",             "stage5")
    g.add_edge("stage5",             "opportunity_scorer")
    g.add_edge("opportunity_scorer", "debate")
    g.add_edge("debate",             "judge")
    g.add_edge("judge",              END)

    return g.compile()


workflow = build_workflow()