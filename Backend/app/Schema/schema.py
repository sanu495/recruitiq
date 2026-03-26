from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime, date

class UserRole(str, Enum):
    admin = "admin"
    recruiter = "recruiter"
    candidate = "candidate"
 
 
class JobStatus(str, Enum):
    open = "open"
    closed = "closed"
    paused = "paused"
 
 
class JobType(str, Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"
 
 
class AppStage(str, Enum):
    applied = "applied"
    screening = "screening"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    rejected = "rejected"
 
 
class InterviewStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
 
 
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = None
    hashed_password: str
    role: UserRole = UserRole.candidate
    is_active: bool = True
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
 
 
class Job(SQLModel, table=True):
    __tablename__ = "jobs"
    id: Optional[int] = Field(default=None, primary_key=True)
    recruiter_id: int = Field(foreign_key="users.id")
    title: str
    description: str
    required_skills: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType = JobType.full_time
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_years: int = 0
    deadline: Optional[date] = None
    status: JobStatus = JobStatus.open
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
 
 
class Application(SQLModel, table=True):
    __tablename__ = "applications"
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="jobs.id")
    candidate_id: int = Field(foreign_key="users.id")
    cover_letter: Optional[str] = None
    resume_path: Optional[str] = None
    resume_text: Optional[str] = None
    stage: AppStage = AppStage.applied
    ai_score: Optional[int] = None
    ai_feedback: Optional[str] = None
    applied_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
 
 
class CandidateNote(SQLModel, table=True):
    __tablename__ = "candidate_notes"
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="applications.id")
    recruiter_id: int = Field(foreign_key="users.id")
    note: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
 
 
class InterviewSlot(SQLModel, table=True):
    __tablename__ = "interview_slots"
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="applications.id")
    scheduled_at: datetime
    duration_minutes: int = 60
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    status: InterviewStatus = InterviewStatus.scheduled
    notes: Optional[str] = None
    created_by: int = Field(foreign_key="users.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
 
 
class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    message: str
    is_read: bool = False
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
