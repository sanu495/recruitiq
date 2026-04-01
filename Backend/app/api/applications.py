from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List
from datetime import datetime
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from Backend.app.core.database import get_session
from Backend.app.core.security import get_current_user, require_role
from Backend.app.core.genericdal import GenericDal
from Backend.app.Schema.schema import Application, Job, User, Notification, CandidateNote
from Backend.app.Models.models import ApplicationOut, NoteCreate, NoteOut
from Backend.app.Services.pdf_parser import extract_text_from_pdf
from Backend.app.Services.ai_screening import screen_resume, get_detailed_analysis, get_recommendation
from Backend.app.core.config import settings
import os
import shutil
import csv
import io

router = APIRouter(prefix="/api/applications", tags=["Applications"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# ── Apply to a Job (Candidate only) ───────────────────────────────────────────

@router.post("", response_model=ApplicationOut)
async def apply_to_job(job_id: int = Form(...), cover_letter: str = Form(""), resume: UploadFile = File(...), 
                       current_user: User = Depends(require_role("candidate")), session: Session = Depends(get_session)):
    # Check job exists and is open
    job_dal = GenericDal(Job, session)
    job = job_dal.get(job_id)

    if job.status != "open":
        raise HTTPException(status_code=400, detail="This Job is no longer accepting application")
    
    # Check if already applied

    app_dal = GenericDal(Application, session)
    existing = session.exec(select(Application).where(Application.job_id == job_id, Application.candidate_id == current_user.id)).first()

    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this job")
    
    # Validate file type
    allowed = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if resume.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF and Word Documents are allowed")
    
    # Save resume file

    file_ext = resume.filename.split(".")[-1]
    filename = f"{current_user.id}_{job_id}_{int(datetime.utcnow().timestamp())}.{file_ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    # Extract text from PDF for AI screening
    resume_text = None
    if file_ext.lower() == "pdf":
        try:
            resume_text = extract_text_from_pdf(filepath)
        except Exception:
            pass

    # AI Screening (Phase 4 — Groq)
    ai_score = None
    ai_feedback = None

    if resume_text and settings.GROQ_API_KEY:
        try:
            ai_score, ai_feedback = await screen_resume(resume_text, job.description, job.required_skills or "")

        except Exception:
            pass

    # Create application
    application = Application(
        job_id=job_id,
        candidate_id=current_user.id,
        cover_letter=cover_letter,
        resume_path=filepath,
        resume_text=resume_text,
        ai_score=ai_score,
        ai_feedback=ai_feedback,
    )
    app_dal.create(application)

    # Notify recruiter
    notif_dal = GenericDal(Notification, session)
    notif_dal.create(Notification(user_id=job.recruiter_id, message=f"New application for '{job.title}' from {current_user.name}"))

    return application

# ── My Applications (Candidate) ────────────────────────────────────────────────

@router.get("/my", response_model=List[ApplicationOut])
def my_application(current_user: User = Depends(require_role("candidate")), session: Session = Depends(get_session)):
    dal = GenericDal(Application, session)
    return dal.get_many_by_field("candidate_id", current_user.id)

# ── All Applications for a Job (Recruiter) ────────────────────────────────────

@router.get("/job/{job_id}", response_model=List[ApplicationOut])
def applications_for_job(job_id: int,_: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    dal = GenericDal(Application, session)
    return dal.get_many_by_field("job_id", job_id)

# ── Get Single Application ─────────────────────────────────────────────────────

@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    dal = GenericDal(Application, session)
    app = dal.get(app_id)

    # Candidate can only see their own
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if current_user.role == "candidate" and app.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
   
    return app

# ── Withdraw Application (Candidate) ──────────────────────────────────────────

@router.delete("/{app_id}")
def withdraw_application(app_id: int, current_user: User = Depends(require_role("candidate")), session: Session = Depends(get_session)):
    dal = GenericDal(Application, session)
    app = dal.get(app_id)

    if app.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your application")

    if app.stage not in ("applied", "screening"):
        raise HTTPException(status_code=400, detail="cannot withdraw at this stage")
    
    dal.delete(app_id)
    return {"message" : "Application withdrawn successfully"}

# ── Add Recruiter Note ─────────────────────────────────────────────────────────

@router.post("/{app_id}/notes", response_model=NoteOut)
def add_note(app_id: int, data: NoteCreate, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    app_dal = GenericDal(Application, session)
    app_dal.get(app_id)        # validates application exists

    note_dal = GenericDal(CandidateNote, session)
    note = CandidateNote(application_id = app_id, recruiter_id = current_user.id, note = data.note)
    return note_dal.create(note)

# ── Get Notes for Application ──────────────────────────────────────────────────

@router.get("/{app_id}/notes", response_model=List[NoteOut])
def get_notes(app_id: int, _: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    note_dal = GenericDal(CandidateNote, session)
    return note_dal.get_many_by_field("application_id", app_id)

# ── Export Applicants as CSV ───────────────────────────────────────────────────

@router.get("/job/{job_id}/export")
def export_csv(job_id: int, _: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    dal = GenericDal(Application, session)
    apps = dal.get_many_by_field("job_id", job_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Application ID", "Candidate ID", "Stage", "AI Score", "AI Feedback", "Applied At"])

    for a in apps:
        writer.writerow([ a.id, a.candidate_id, a.stage, a.ai_score or "N/A", a.ai_feedback or "N/A", a.applied_at])

    output.seek(0)   
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=job_{job_id}_applicants.csv"}) 

# ── Trigger AI Screening Manually (Recruiter) ─────────────────────────────────

@router.post("/{app_id}/screen")
async def trigger_ai_screening(app_id: int, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    """Manually trigger AI screening for an application."""

    dal = GenericDal(Application, session)
    app = dal.get(app_id)

    if not app.resume_text:
        raise HTTPException(status_code=400, detail="No resume text found. PDF may not be parseable.")
    
    job_dal = GenericDal(Job, session)
    job = job_dal.get(app.job_id)

    ai_score, ai_feedback = await screen_resume(app.resume_text, job.description, job.required_skills or "")

    if ai_score is None:
        raise HTTPException(status_code=503, detail="AI screening unavailable. Check GROQ_API_KEY.")
    
    updated = dal.update(app_id, {"ai_score": ai_score, "ai_feedback": ai_feedback})
    return {"application_id": app_id, "ai_score": ai_score, "ai_feedback": ai_feedback, "recommendation": get_recommendation(ai_score)}

# ── Get Detailed AI Analysis ───────────────────────────────────────────────────

@router.get("/{app_id}/analysis")
async def get_ai_analysis(app_id: int, _: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):

    """Get full detailed AI analysis for a candidate."""
    dal = GenericDal(Application, session)
    app = dal.get(app_id)
 
    if not app.resume_text:
        raise HTTPException(status_code=400, detail="No resume text available.")
 
    job_dal = GenericDal(Job, session)
    job = job_dal.get(app.job_id)

    analysis = await get_detailed_analysis(app.resume_text, job.description, job.required_skills or "")

    if not analysis:
        raise HTTPException(status_code=503, detail="AI analysis unavailable.")
 
    return analysis





    

    

 


