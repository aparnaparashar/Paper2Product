"""
Pipeline runner — uses FastAPI BackgroundTasks.
Parallel stages run inside workflow.py via ThreadPoolExecutor.
Worker just streams progress per stage.
"""
import time
from datetime import datetime
from app.core.database import SessionLocal
from app.core.cache import set_progress, delete_progress
from app.models.project import Project
from app.graph.workflow import workflow

# Maps the node name that LangGraph emits → DB field to write + progress %
# Stage nodes write multiple fields; we map the stage key to progress only.
# Individual agent outputs are written inside _run_parallel via state.update().
STAGE_PROGRESS = {
    "research_analyst":   ("research_profile",  7),
    "stage2":             (None,                21),   # tech_validator + market_discovery
    "stage3":             (None,                35),   # customer_persona + competitor_intel + knowledge_graph
    "stage4":             (None,                56),   # product_strategist + risk_analyst + investment_agent
    "stage5":             (None,                70),   # mvp_planner + architect + revenue_strategy
    "opportunity_scorer": ("opportunity_scores", 82),
    "debate":             ("debate_transcript",  93),
    "judge":              ("final_report",       100),
}

# All state keys that hold agent outputs — written after each stage completes
ALL_OUTPUT_FIELDS = [
    "research_profile", "innovation_score", "market_opportunities",
    "customer_personas", "competitive_landscape", "product_concepts",
    "mvp_plan", "architecture", "revenue_strategy", "risk_profile",
    "investment_score", "knowledge_graph", "opportunity_scores",
    "debate_transcript", "final_report",
]

STAGE_LABELS = {
    "research_analyst":   "Research Analyst",
    "stage2":             "Technical Validator + Market Discovery",
    "stage3":             "Customer Personas + Competitors + Knowledge Graph",
    "stage4":             "Product Strategy + Risk + Investment",
    "stage5":             "MVP + Architecture + Revenue",
    "opportunity_scorer": "Opportunity Scorer",
    "debate":             "Agent Debate",
    "judge":              "Judge Agent",
}


def run_analysis(project_id: str, raw_text: str):
    db = SessionLocal()
    project = None
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return

        project.status = "processing"
        db.commit()

        state = {
            "project_id": project_id,
            "raw_text": raw_text,
            "research_profile": None,
            "innovation_score": None,
            "market_opportunities": None,
            "customer_personas": None,
            "competitive_landscape": None,
            "product_concepts": None,
            "mvp_plan": None,
            "architecture": None,
            "revenue_strategy": None,
            "risk_profile": None,
            "investment_score": None,
            "knowledge_graph": None,
            "opportunity_scores": None,
            "debate_transcript": None,
            "final_report": None,
            "agent_metadata": {},
            "awaiting_hitl": None,
            "hitl_approved": None,
            "hitl_feedback": None,
            "error": None,
        }

        total_tokens = 0
        total_cost   = 0.0
        t_start      = time.time()

        for step_output in workflow.stream(state):
            for node_name, node_state in step_output.items():
                db.refresh(project)

                # Write all output fields that were populated in this stage
                for field in ALL_OUTPUT_FIELDS:
                    val = node_state.get(field)
                    if val is not None:
                        setattr(project, field, val)

                # Accumulate cost/token metrics from all agents in this stage
                for agent_meta in (node_state.get("agent_metadata") or {}).values():
                    total_tokens += agent_meta.get("total_tokens", 0) or 0
                    total_cost   += agent_meta.get("estimated_cost_usd", 0.0) or 0.0

                _, progress = STAGE_PROGRESS.get(node_name, (None, 0))
                label = STAGE_LABELS.get(node_name, node_name)
                project.current_agent = label
                project.progress      = str(progress)
                db.commit()

                set_progress(project_id, {
                    "status":        "processing",
                    "current_agent": label,
                    "progress":      str(progress),
                })

                state.update(node_state)

        project.status             = "completed"
        project.current_agent      = None
        project.progress           = "100"
        project.completed_at       = datetime.utcnow()
        project.total_tokens       = {"total": total_tokens}
        project.total_cost_usd     = round(total_cost, 4)
        project.total_duration_sec = round(time.time() - t_start, 2)
        db.commit()

        set_progress(project_id, {"status": "completed", "current_agent": None, "progress": "100"})

    except Exception as e:
        if project:
            try:
                db.refresh(project)
                project.status        = "failed"
                project.error_message = str(e)[:1000]
                db.commit()
            except Exception:
                pass
        set_progress(project_id, {"status": "failed", "current_agent": None, "progress": "0"})
        raise
    finally:
        db.close()
        delete_progress(project_id)