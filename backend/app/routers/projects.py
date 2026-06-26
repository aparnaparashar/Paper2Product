import uuid, json, time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.cache import get_progress
from app.models.user import User
from app.models.project import Project
from app.models.agent_run import AgentRun
from app.schemas.schemas import (
    ProjectStatusResponse, ProjectReportResponse,
    ProjectListItem, AgentRunResponse, HITLDecision,
)
from app.services.ingestion import extract_text, save_upload, store_embeddings
from app.services.export import export_markdown, export_pdf, export_docx
from app.worker import run_analysis

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ── Create + start pipeline ───────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_project(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    title: str = Form("Untitled Project"),
    abstract: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_id = str(uuid.uuid4())
    raw_text = ""
    file_name = None

    if file and file.filename:
        file_bytes = await file.read()
        file_name = file.filename
        save_upload(project_id, file_name, file_bytes)
        raw_text = extract_text(file_name, file_bytes)
        store_embeddings(project_id, raw_text)
    elif abstract:
        raw_text = abstract
    else:
        raise HTTPException(400, "Provide a file or abstract text")

    if len(raw_text.strip()) < 100:
        raise HTTPException(400, "Document too short to analyse (min 100 chars)")

    project = Project(
        id=project_id,
        user_id=current_user.id,
        title=title or file_name or "Untitled Project",
        raw_text=raw_text,
        file_name=file_name,
        status="pending",
    )
    db.add(project); db.commit()

    background_tasks.add_task(run_analysis, project_id, raw_text)
    return {"project_id": project_id, "status": "processing"}


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[ProjectListItem])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
def get_status(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not p: raise HTTPException(404, "Not found")
    return p


# ── Report ────────────────────────────────────────────────────────────────────

@router.get("/portfolio/ranked")
def portfolio_ranked(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Feature 4 — rank all completed projects by opportunity score."""
    projects = db.query(Project).filter(
        Project.user_id == current_user.id,
        Project.status == "completed",
    ).all()
    ranked = []
    for p in projects:
        opp = p.opportunity_scores or {}
        inv = p.investment_score or {}
        fr  = p.final_report or {}
        mo  = p.market_opportunities or {}
        risk= p.risk_profile or {}
        ranked.append({
            "project_id":    p.id,
            "title":         p.title,
            "final_score":   opp.get("weighted_final_score"),
            "investment_score": inv.get("investment_score"),
            "market_size":   (mo.get("primary_market") or {}).get("size_usd_billion"),
            "risk_level":    risk.get("overall_risk_level"),
            "go_no_go":      fr.get("go_no_go"),
            "created_at":    p.created_at,
        })
    ranked.sort(key=lambda x: x["final_score"] or 0, reverse=True)
    return ranked


@router.get("/{project_id}/report", response_model=ProjectReportResponse)
def get_report(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not p: raise HTTPException(404, "Not found")
    if p.status not in ("completed", "failed"): raise HTTPException(202, "Still processing")
    return p


# ── Agent traceability (Feature 1 + 9) ───────────────────────────────────────

@router.get("/{project_id}/agents", response_model=List[AgentRunResponse])
def get_agent_runs(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not p: raise HTTPException(404, "Not found")
    return db.query(AgentRun).filter(AgentRun.project_id == project_id).order_by(AgentRun.created_at).all()


# ── SSE progress stream (uses Upstash Redis cache) ────────────────────────────

@router.get("/{project_id}/stream")
def stream_progress(
    project_id: str,
    token: str = None,          # EventSource can't set headers — accept token as query param
    db: Session = Depends(get_db),
):
    # Validate token manually since EventSource can't send Authorization header
    from app.core.auth import get_current_user
    from fastapi.security import OAuth2PasswordBearer
    from fastapi import Request
    from app.core.config import get_settings
    from jose import jwt, JWTError
    from app.models.user import User as UserModel

    settings = get_settings()
    user_id = None
    if token:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("sub")
        except JWTError:
            pass
    if not user_id:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    p = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not p: raise HTTPException(404, "Not found")

    def generate():
        while True:
            # Try Upstash Redis first, fall back to DB poll
            cached = get_progress(project_id)
            if cached:
                data = cached
            else:
                db.expire_all()
                proj = db.query(Project).filter(Project.id == project_id).first()
                if not proj: break
                data = {"status": proj.status, "current_agent": proj.current_agent, "progress": proj.progress}

            yield f"data: {json.dumps(data)}\n\n"
            if data.get("status") in ("completed", "failed"):
                break
            time.sleep(2)

    return StreamingResponse(generate(), media_type="text/event-stream",
                              headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── Human-in-the-Loop (Feature 8) ────────────────────────────────────────────

@router.post("/{project_id}/hitl")
def submit_hitl(
    project_id: str,
    decision: HITLDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not p: raise HTTPException(404, "Not found")
    if p.status != "awaiting_hitl": raise HTTPException(400, "Project not awaiting review")
    p.status = "processing"
    p.hitl_pending_agent = None
    p.hitl_pending_data  = None
    db.commit()
    return {"message": "Decision recorded — pipeline resumed"}


# ── Export (Feature 5) ────────────────────────────────────────────────────────

@router.get("/{project_id}/export/{fmt}")
def export_report(
    project_id: str,
    fmt: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not p: raise HTTPException(404, "Not found")
    if p.status != "completed": raise HTTPException(400, "Report not ready")

    slug = p.title.replace(" ", "_")[:40]
    if fmt == "markdown":
        return Response(export_markdown(p).encode(), media_type="text/markdown",
                        headers={"Content-Disposition": f'attachment; filename="{slug}.md"'})
    elif fmt == "pdf":
        return Response(export_pdf(p), media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="{slug}.pdf"'})
    elif fmt == "docx":
        return Response(export_docx(p),
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"Content-Disposition": f'attachment; filename="{slug}.docx"'})
    raise HTTPException(400, f"Unknown format. Use: markdown, pdf, docx")


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not p: raise HTTPException(404, "Not found")
    db.query(AgentRun).filter(AgentRun.project_id == project_id).delete()
    db.delete(p); db.commit()