from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from Backend.app.core.database import get_session
from Backend.app.core.security import get_current_user, require_role
from Backend.app.core.genericdal import GenericDal
from Backend.app.Models.models import JobCreate, JobUpdate, JobOut
from Backend.app.Schema.schema import Job, User, JobStatus

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

# ── Create Job (Recruiter / Admin only) ────────────────────────────────────────

@router.post("", response_model=JobOut)
def create_job(data: JobCreate, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    job = Job(**data.dict(), recruiter_id=current_user.id)
    dal = GenericDal(Job, session)
    return dal.create(job)

# ── List All Jobs (with search + filter) ──────────────────────────────────────

@router.get("", response_model=List[JobOut])
def list_jobs(search: Optional[str] = Query(None, description="Search by title  or skill"), 
              location: Optional[str] = Query(None),
              job_type: Optional[str] = Query(None),
              min_salary: Optional[float] = Query(None),
              status: Optional[str] = Query("open"),
              _: User = Depends(get_current_user), session: Session = Depends(get_session)):
    
    query = select(Job)

    
    # Filters
    if status:
        query = query.where(Job.status == status)
    if location:
        query = query.where(Job.location.contains(location))
    if job_type:
        query = query.where(Job.job_type == job_type)
    if min_salary:
        query = query.where(Job.salary_min >= min_salary)
    if search:
        query = query.where(
            (Job.title.contains(search)) |
            (Job.required_skills.contains(search))
        )
 
    query = query.order_by(Job.created_at.desc())
    jobs = session.exec(query).all()
 
    # Auto-close expired jobs
    today = date.today()
    for job in jobs:
        if job.deadline and job.deadline < today and job.status == JobStatus.open:
            job.status = JobStatus.closed
            session.add(job)
    session.commit()
 
    return jobs

    