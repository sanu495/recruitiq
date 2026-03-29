from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from Backend.app.core.database import get_session
from Backend.app.core.security import get_current_user, require_role
from Backend.app.core.genericdal import GenericDal
from Backend.app.Schema.schema import Application, Job, User, Notification
from Backend.app.Models.models import ApplicationOut, StageUpdate

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])

# Stage messages sent to candidates on every update
STAGE_MESSAGES = {
    "screening": "Your application is being reviewed by our team.",
    "interview": "Congratulations! You have been shortlisted for an interview.",
    "offer":     "Great news! We are preparing an offer for you.",
    "hired":     "Congratulations! You have been selected for this position!",
    "rejected":  "Thank you for applying. We will keep your profile for future opportunities.",
}

# ── Get Full Pipeline for a Job ────────────────────────────────────────────────

@router.get("/job/{job_id}", response_model=List[ApplicationOut])
def get_pipeline(job_id: int, _: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):

    """Returns all applications for a job grouped by stage"""
    dal = GenericDal(Application, session)
    apps = dal.get_many_by_field("job_id", job_id)

    # Sort by stage order
    stage_order = ["applied", "screening", "interview", "offer", "hired", "rejected"]
    return sorted(apps, key=lambda a: stage_order.index(a.stage) if a.stage in stage_order else 99)

 # ── Move Candidate to Next Stage ───────────────────────────────────────────────
   
@router.patch("/{app_id}/stage", response_model=ApplicationOut)
def update_stage(app_id: int, data: StageUpdate, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    app_dal = GenericDal(Application, session)
    application = app_dal.get(app_id)

    # Validate stage transition
    stage_order = ["applied", "screening", "interview", "offer", "hired", "rejected"]
    current_index = stage_order.index(application.stage)
    new_index = stage_order.index(data.stage)

    # Allow any move forward + allow rejected from any stage
    if data.stage != "rejected" and new_index < current_index:
        raise HTTPException(status_code=400, detail=f"Cannot move backwards from '{application.stage}' to '{data.stage}'")
    
    # Update stage
    updated = app_dal.update(app_id, {"stage":data.stage, "updated_at":datetime.utcnow()})

    # Send notification to candidate
    notif_dal = GenericDal(Notification, session)
    message = STAGE_MESSAGES.get(data.stage, f"Your application status updated to: {data.stage.upper()}")

    # Get job title for the notification
    job_dal = GenericDal(Job, session)
    job = job_dal.get(application.job_id)

    notif_dal.create(Notification(user_id=application.candidate_id, message=f"[{job.title}] {message}"))
    return updated

# ── Get Pipeline Summary (Count per stage) ────────────────────────────────────

@router.get("/job/{job_id}/summary")
def pipeline_summary(job_id: int, _: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    
    """Returns count of candidates at each stage"""
    dal = GenericDal(Application, session)
    apps = dal.get_many_by_field("job_id", job_id)

    stages = ["applied", "screening", "interview", "offer", "hired", "rejected"]
    summary = {stage: 0 for stage in stages}

    for app in apps:
        if app.stage in summary:
            summary[app.stage] += 1

    summary["total"] = len(apps)
    return summary

# ── Get All Pipelines (Recruiter overview) ────────────────────────────────────

@router.get("/overview", response_model=List[ApplicationOut])
def all_pipelines(current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):

    """Returns all applications across all jobs posted by this recruiter"""
    if current_user.role == "admin":
        # Admin sees everything
        apps = session.exec(select(Application)).all()
    else:
        # Recruiter sees only their job applications
        jobs = session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()
        job_ids = [j.id for j in jobs]

        if not job_ids:
            return []
        
        apps = session.exec(select(Application).where(Application.job_id.in_(job_ids))).all()
 
    return apps

# ── Bulk Reject Remaining Applicants ──────────────────────────────────────────

@router.patch("/job/{job_id}/bulk-reject")
def bulk_reject(job_id: int, _: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):

    """Reject all 'applied' stage candidates at once"""
    dal = GenericDal(Application, session)
    apps = dal.get_many_by_field("job_id", job_id)

    rejected_count = 0
    notif_dal = GenericDal(Notification, session)
    job_dal = GenericDal(Job, session)
    job = job_dal.get(job_id)

    for app in apps:
        if app.stage == "applied":
            dal.update(app.id, {"stage" : "rejected", "updated_at" : datetime.utcnow()})
            notif_dal.create(Notification(user_id=app.candidate_id, message=f"[{job.title}] {STAGE_MESSAGES['rejected']}"))
            rejected_count += 1

    return {"message" : f"{rejected_count} candidates rejected"}












