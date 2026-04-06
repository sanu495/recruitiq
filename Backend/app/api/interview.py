from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from Backend.app.core.database import get_session
from Backend.app.core.security import get_current_user, require_role
from Backend.app.core.genericdal import GenericDal
from Backend.app.Schema.schema import InterviewSlot, Application, Job, User, Notification
from Backend.app.Models.models import InterviewCreate, InterviewUpdate, InterviewOut

router = APIRouter(prefix="/api/interviews", tags=["Interviews"])

# ── Schedule Interview (Recruiter) ────────────────────────────────────────────

@router.post("", response_model=InterviewOut)
def schedule_interview(data: InterviewCreate, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    """Recruiter schedules an interview for a candidate application."""

    # Validate application exists
    app_dal = GenericDal(Application, session)
    application = app_dal.get(data.application_id)

    # Validate application is in right stage
    if application.stage not in ("applied", "screening", "interview"):
        raise HTTPException(status_code=400, detail=f"Cannot schedule interview for stage: {application.stage}")
    
    # Check no duplicate scheduled interview for same application
    existing = session.exec(select(InterviewSlot).where(InterviewSlot.application_id == data.application_id, InterviewSlot.status == "scheduled")).first()

    if existing:
        raise HTTPException(status_code=400, detail="An interview is already scheduled for this candidate. Update or cancel it first.")
    
    # Create interview slot
    slot_dal = GenericDal(InterviewSlot, session)
    slot = InterviewSlot(**data.dict(), created_by=current_user.id)
    created_slot = slot_dal.create(slot)

    # Auto move application stage to interview
    app_dal.update(application.id, {"stage":"interview"})

    # Notify candidate
    job_dal = GenericDal(Job, session)
    job = job_dal.get(application.job_id)

    notif_dal = GenericDal(Notification, session)

    location_info = f"Location: {data.location}" if data.location else ""
    link_info = f"Meeting link: {data.meeting_link}" if data.meeting_link else ""
    details = " | ".join(filter(None, [location_info, link_info]))
 
    notif_dal.create(Notification(user_id=application.candidate_id, message=(f"[{job.title}] Interview scheduled on " f"{data.scheduled_at.strftime('%d %b %Y at %H:%M')} " f"({data.duration_minutes} min). {details}")))

    return created_slot

# ── Get All Interviews ─────────────────────────────────────────────────────────

@router.get("", response_model=List[InterviewOut])
def list_interviews(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Recruiter/Admin sees all interviews.
    Candidate sees only their own interviews.
    """
    if current_user.role in ("recruiter", "admin"):
        if current_user.role == "admin":
            slots = session.exec(select(InterviewSlot).order_by(InterviewSlot.scheduled_at)).all()
        else:
            # Recruiter sees interviews for their jobs only
            job_ids = [j.id for j in session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()]
            app_ids = [a.id for a in session.exec(select(Application).where(Application.job_id.in_(job_ids))).all()] if job_ids else []
            slots = session.exec(select(InterviewSlot).where(InterviewSlot.application_id.in_(app_ids)).order_by(InterviewSlot.scheduled_at)).all() if app_ids else []
 
    else:
        # Candidate sees their own interviews only
        app_ids = [a.id for a in session.exec(select(Application).where(Application.candidate_id == current_user.id)).all()]
        slots = session.exec(select(InterviewSlot).where(InterviewSlot.application_id.in_(app_ids)).order_by(InterviewSlot.scheduled_at)).all() if app_ids else []
 
    return slots

# ── Get Upcoming Interviews ────────────────────────────────────────────────────

@router.get("/upcoming/list", response_model=List[InterviewOut])
def upcoming_interviews(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Returns only upcoming (not cancelled/completed) interviews."""
 
    if current_user.role in ("recruiter", "admin"):
        slots = session.exec(select(InterviewSlot).where(InterviewSlot.scheduled_at >= datetime.utcnow(), InterviewSlot.status.in_(["scheduled", "confirmed"])).order_by(InterviewSlot.scheduled_at)).all()

    else:
        app_ids = [a.id for a in session.exec(select(Application).where(Application.candidate_id == current_user.id)).all()]
        slots = session.exec(select(InterviewSlot).where(InterviewSlot.application_id.in_(app_ids),InterviewSlot.scheduled_at >= datetime.utcnow(),InterviewSlot.status.in_(["scheduled", "confirmed"])).order_by(InterviewSlot.scheduled_at)).all() if app_ids else []
 
    return slots

# ── Get Single Interview ───────────────────────────────────────────────────────

@router.get("/{slot_id}", response_model=InterviewOut)
def get_interview(slot_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    dal = GenericDal(InterviewSlot, session)
    slot = dal.get(slot_id)

    # Candidate can only see their own
    if current_user.role == "candidate":
        app_dal = GenericDal(Application, session)
        application = app_dal.get(slot.application_id)

        if application.candidate_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
    return slot

# ── Update Interview (Recruiter) ───────────────────────────────────────────────

@router.put("/{slot_id}", response_model=InterviewOut)
def update_interview(slot_id: int, data: InterviewUpdate, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    
    """Recruiter updates interview time, link, location, or status."""

    dal = GenericDal(InterviewSlot, session)
    slot = dal.get(slot_id)
 
    updated = dal.update(slot_id, data.dict(exclude_none=True))
 
    # Notify candidate about changes
    app_dal = GenericDal(Application, session)
    application = app_dal.get(slot.application_id)
 
    job_dal = GenericDal(Job, session)
    job = job_dal.get(application.job_id)
 
    notif_dal = GenericDal(Notification, session)
 
    if data.scheduled_at:
        notif_dal.create(Notification(user_id=application.candidate_id, message=(f"[{job.title}] Your interview has been rescheduled to " f"{data.scheduled_at.strftime('%d %b %Y at %H:%M')}.")))
    
    elif data.status:
        status_messages = {
            "confirmed":  "Your interview has been confirmed.",
            "completed":  "Your interview has been marked as completed.",
            "cancelled":  "Your interview has been cancelled. Please check for updates."}
        
        msg = status_messages.get(data.status, f"Interview status updated to: {data.status}")
        notif_dal.create(Notification(user_id=application.candidate_id, message=f"[{job.title}] {msg}"))
 
    return updated
 
# ── Candidate Confirms Interview ───────────────────────────────────────────────

@router.patch("/{slot_id}/confirm", response_model=InterviewOut)
def confirm_interview(slot_id: int, current_user: User = Depends(require_role("candidate")), session: Session = Depends(get_session)):
    """Candidate confirms they will attend the interview."""
    dal = GenericDal(InterviewSlot, session)
    slot = dal.get(slot_id)
 
    # Verify this interview belongs to this candidate
    app_dal = GenericDal(Application, session)
    application = app_dal.get(slot.application_id)
 
    if application.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your interview")
 
    if slot.status != "scheduled":
        raise HTTPException(status_code=400, detail=f"Cannot confirm interview with status: {slot.status}")
 
    updated = dal.update(slot_id, {"status": "confirmed"})
 
    # Notify recruiter
    job_dal = GenericDal(Job, session)
    job = job_dal.get(application.job_id)
 
    notif_dal = GenericDal(Notification, session)
    notif_dal.create(Notification(user_id=slot.created_by, message=(f"{current_user.name} has confirmed their interview for " f"'{job.title}' on {slot.scheduled_at.strftime('%d %b %Y at %H:%M')}.")))
 
    return updated
 
 
# ── Cancel Interview ───────────────────────────────────────────────────────────

@router.patch("/{slot_id}/cancel", response_model=InterviewOut)
def cancel_interview(slot_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Recruiter or Candidate can cancel an interview."""

    dal = GenericDal(InterviewSlot, session)
    slot = dal.get(slot_id)
 
    if slot.status in ("completed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Interview is already {slot.status}")
 
    updated = dal.update(slot_id, {"status": "cancelled"})
 
    # Notify the other party
    app_dal = GenericDal(Application, session)
    application = app_dal.get(slot.application_id)
 
    job_dal = GenericDal(Job, session)
    job = job_dal.get(application.job_id)
 
    notif_dal = GenericDal(Notification, session)
 
    if current_user.role == "candidate":
        # Notify recruiter
        notif_dal.create(Notification(user_id=slot.created_by,message=(f"{current_user.name} has cancelled their interview for '{job.title}'.")))
    else:
        # Notify candidate
        notif_dal.create(Notification(user_id=application.candidate_id, message=(f"[{job.title}] Your interview scheduled on " f"{slot.scheduled_at.strftime('%d %b %Y at %H:%M')} " f"has been cancelled.")))
 
    return updated











    




