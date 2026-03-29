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

# ── Get Single Job ─────────────────────────────────────────────────────────────

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, _: User = Depends(get_session), session: Session = Depends(get_session)):
    dal = GenericDal(Job, session)
    return dal.get(job_id)

# ── Update Job (Recruiter who posted it / Admin) ───────────────────────────────

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, data: JobUpdate, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    dal = GenericDal(job, session)
    job = dal.get(job_id)

    # Only the recruiter who posted it or admin can update

    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only update your own jobs")
    
    job.updated_at = datetime.utcnow()
    return dal.update(job_id, data.dict(exclude_none=True))

# ── Delete Job ─────────────────────────────────────────────────────────────────

@router.delete("/{job_id}")
def delete_job(job_id: int, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    dal = GenericDal(Job, session)
    job = dal.get(job_id)

    if job.recruiter != current_user.id and current_user.role !="admin":
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")
    
    dal.delete(job_id)
    return {"message":"Job deleted successfully"}

# ── My Posted Jobs (Recruiter) ─────────────────────────────────────────────────

@router.get("/my/posted", response_model=List[JobOut])
def my_posted_jobs(current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    dal = GenericDal(Job, session)
    return dal.get_many_by_field("recruiter_id", current_user.id)

# ── Close / Pause / Reopen Job ─────────────────────────────────────────────────

@router.patch("/{job_id}/status", response_model=JobOut)
def change_job_status(job_id: int, status: JobStatus, current_user: User = Depends(require_role("recruiter", "admin")), session: Session = Depends(get_session)):
    dal = GenericDal(Job, session)
    job = dal.get(job_id)

    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your job")
    
    return dal.update(job_id, {"status": status, "updated_at": datetime.utcnow()})

   