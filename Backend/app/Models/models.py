from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from Backend.app.Schema.schema import UserRole, JobType, JobStatus, AppStage, InterviewStatus


# ══════════════════════════════════════════════════
#  AUTH SCHEMAS
# ══════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: UserRole = UserRole.candidate


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
#  JOB SCHEMAS
# ══════════════════════════════════════════════════

class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType = JobType.full_time
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_years: int = 0
    deadline: Optional[date] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_years: Optional[int] = None
    deadline: Optional[date] = None
    status: Optional[JobStatus] = None


class JobOut(BaseModel):
    id: int
    recruiter_id: int
    title: str
    description: str
    required_skills: Optional[str]
    location: Optional[str]
    job_type: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    experience_years: int
    deadline: Optional[date]
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
#  APPLICATION SCHEMAS
# ══════════════════════════════════════════════════

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    cover_letter: Optional[str]
    resume_path: Optional[str]
    stage: str
    ai_score: Optional[int]
    ai_feedback: Optional[str]
    applied_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class StageUpdate(BaseModel):
    stage: AppStage


# ══════════════════════════════════════════════════
#  CANDIDATE NOTE SCHEMAS
# ══════════════════════════════════════════════════

class NoteCreate(BaseModel):
    note: str


class NoteOut(BaseModel):
    id: int
    application_id: int
    recruiter_id: int
    note: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
#  INTERVIEW SCHEMAS
# ══════════════════════════════════════════════════

class InterviewCreate(BaseModel):
    application_id: int
    scheduled_at: datetime
    duration_minutes: int = 60
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class InterviewUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    status: Optional[InterviewStatus] = None
    notes: Optional[str] = None


class InterviewOut(BaseModel):
    id: int
    application_id: int
    scheduled_at: datetime
    duration_minutes: int
    meeting_link: Optional[str]
    location: Optional[str]
    status: str
    notes: Optional[str]
    created_by: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
#  NOTIFICATION SCHEMAS
# ══════════════════════════════════════════════════

class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True