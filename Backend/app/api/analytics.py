from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from Backend.app.core.database import get_session
from Backend.app.core.security import require_role
from Backend.app.core.genericdal import GenericDal
from Backend.app.Schema.schema import Job, Application, User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# ── Overview Dashboard Stats ───────────────────────────────────────────────────

@router.get("/overview")
def overview(
    current_user: User = Depends(require_role("recruiter", "admin")),
    session: Session = Depends(get_session)
):
    if current_user.role == "admin":
        total_jobs       = session.exec(select(func.count(Job.id))).one()
        open_jobs        = session.exec(select(func.count(Job.id)).where(Job.status == "open")).one()
        total_apps       = session.exec(select(func.count(Application.id))).one()
        total_candidates = session.exec(select(func.count(func.distinct(Application.candidate_id)))).one()
        hired_count      = session.exec(select(func.count(Application.id)).where(Application.stage == "hired")).one()
    else:
        job_ids    = [j.id for j in session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()]
        total_jobs = len(job_ids)
        open_jobs  = session.exec(select(func.count(Job.id)).where(Job.recruiter_id == current_user.id, Job.status == "open")).one()

        if not job_ids:
            return {"total_jobs": 0, "open_jobs": 0, "total_applications": 0, "total_candidates": 0, "hired_count": 0, "conversion_rate": 0}

        total_apps       = session.exec(select(func.count(Application.id)).where(Application.job_id.in_(job_ids))).one()
        total_candidates = session.exec(select(func.count(func.distinct(Application.candidate_id))).where(Application.job_id.in_(job_ids))).one()
        hired_count      = session.exec(select(func.count(Application.id)).where(Application.job_id.in_(job_ids), Application.stage == "hired")).one()

    conversion_rate = round((hired_count / total_apps * 100), 1) if total_apps > 0 else 0

    return {
        "total_jobs":         total_jobs,
        "open_jobs":          open_jobs,
        "total_applications": total_apps,
        "total_candidates":   total_candidates,
        "hired_count":        hired_count,
        "conversion_rate":    conversion_rate,
    }

# ── Pipeline Breakdown ─────────────────────────────────────────────────────────

@router.get("/pipeline-breakdown")
def pipeline_breakdown(
    current_user: User = Depends(require_role("recruiter", "admin")),
    session: Session = Depends(get_session)
):
    stages = ["applied", "screening", "interview", "offer", "hired", "rejected"]

    if current_user.role == "admin":
        apps = session.exec(select(Application)).all()
    else:
        job_ids = [j.id for j in session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()]
        apps    = session.exec(select(Application).where(Application.job_id.in_(job_ids))).all() if job_ids else []

    result = {stage: 0 for stage in stages}
    for app in apps:
        if app.stage in result:
            result[app.stage] += 1

    return result

# ── Applications Per Job ───────────────────────────────────────────────────────

@router.get("/applications-per-job")
def applications_per_job(
    current_user: User = Depends(require_role("recruiter", "admin")),
    session: Session = Depends(get_session)
):
    if current_user.role == "admin":
        jobs = session.exec(select(Job)).all()
    else:
        jobs = session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()

    data = []
    for job in jobs:
        count = session.exec(select(func.count(Application.id)).where(Application.job_id == job.id)).one()
        data.append({
            "job_id":           job.id,
            "job_title":        job.title,
            "total_applicants": count,
            "status":           job.status,
        })

    return sorted(data, key=lambda x: x["total_applicants"], reverse=True)

# ── AI Score Distribution ──────────────────────────────────────────────────────

@router.get("/ai-score-distribution")
def ai_score_distribution(
    current_user: User = Depends(require_role("recruiter", "admin")),
    session: Session = Depends(get_session)
):
    if current_user.role == "admin":
        apps = session.exec(select(Application).where(Application.ai_score != None)).all()
    else:
        job_ids = [j.id for j in session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()]
        apps    = session.exec(select(Application).where(Application.job_id.in_(job_ids), Application.ai_score != None)).all() if job_ids else []

    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for app in apps:
        score = app.ai_score
        if   score <= 20: buckets["0-20"]   += 1
        elif score <= 40: buckets["21-40"]  += 1
        elif score <= 60: buckets["41-60"]  += 1
        elif score <= 80: buckets["61-80"]  += 1
        else:             buckets["81-100"] += 1

    return buckets

# ── Top Candidates by AI Score ────────────────────────────────────────────────

@router.get("/top-candidates")
def top_candidates(
    job_id: int = None,
    limit: int = 10,
    current_user: User = Depends(require_role("recruiter", "admin")),
    session: Session = Depends(get_session)
):
    query = select(Application).where(Application.ai_score != None)

    if job_id:
        query = query.where(Application.job_id == job_id)
    elif current_user.role != "admin":
        job_ids = [j.id for j in session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()]
        if not job_ids:
            return []
        query = query.where(Application.job_id.in_(job_ids))

    apps   = session.exec(query.order_by(Application.ai_score.desc()).limit(limit)).all()
    result = []

    for app in apps:
        user = session.get(User, app.candidate_id)
        job  = session.get(Job,  app.job_id)
        result.append({
            "application_id":  app.id,
            "job_id":          app.job_id,          # ← FIX: was missing → caused job_id=undefined in View button
            "candidate_name":  user.name  if user else "Unknown",
            "candidate_email": user.email if user else "Unknown",
            "job_title":       job.title  if job  else "Unknown",
            "ai_score":        app.ai_score,
            "ai_feedback":     app.ai_feedback,
            "stage":           app.stage,
            "applied_at":      app.applied_at,
        })

    return result

# ── Monthly Applications Trend ─────────────────────────────────────────────────

@router.get("/monthly-trend")
def monthly_trend(
    current_user: User = Depends(require_role("recruiter", "admin")),
    session: Session = Depends(get_session)
):
    if current_user.role == "admin":
        apps = session.exec(select(Application)).all()
    else:
        job_ids = [j.id for j in session.exec(select(Job).where(Job.recruiter_id == current_user.id)).all()]
        apps    = session.exec(select(Application).where(Application.job_id.in_(job_ids))).all() if job_ids else []

    monthly = {}
    for app in apps:
        if app.applied_at:
            key          = app.applied_at.strftime("%Y-%m")
            monthly[key] = monthly.get(key, 0) + 1

    return [{"month": m, "applications": c} for m, c in sorted(monthly.items())]