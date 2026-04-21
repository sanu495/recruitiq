from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from Backend.app.api import (applications, analytics, auth, interview, jobs, notification, pipeline)
from Backend.app.core.config import settings as _s
from Backend.app.core.database import create_db_and_tables
import os 

app = FastAPI(
    title="RecruitIQ API",
    description="AI-powered Applicant Tracking System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = getattr(_s, "UPLOAD_DIR", None) or "uploads"

try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError as exc:
    raise RuntimeError(f"Could not create upload directory: {UPLOAD_DIR}") from exc

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(pipeline.router)
app.include_router(notification.router)
app.include_router(analytics.router)
app.include_router(interview.router)

NO_CACHE = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}

def page(path: str) -> FileResponse:
    return FileResponse(path, headers=NO_CACHE)

@app.get("/")
def home():
    return page("Frontend/home.html")

@app.get("/login")
def login_page():
    return page("Frontend/index.html")

@app.get("/index.html")
def index_page():
    return page("Frontend/index.html")

@app.get("/dashboard/recruiter")
def recruiter_dashboard():
    return page("Frontend/dashboard/recruiter.html")

@app.get("/dashboard/candidate")
def candidate_dashboard():
    return page("Frontend/dashboard/candidate.html")

@app.get("/jobs")
def jobs_page():
    return page("Frontend/pages/jobs.html")

@app.get("/pipeline")
def pipeline_page():
    return page("Frontend/pages/pipeline.html")

@app.get("/analytics")
def analytics_page():
    return page("Frontend/pages/analytics.html")

@app.get("/interviews")
def interviews_page():
    return page("Frontend/pages/interviews.html")

@app.get("/applications")
def applications_page():
    return page("Frontend/pages/applications.html")

@app.get("/notifications")
def notifications_page():
    return page("Frontend/pages/notifications.html")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/css", StaticFiles(directory="Frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="Frontend/js"), name="js")
app.mount("/favicon", StaticFiles(directory="Frontend/favicon"), name="favicon")
app.mount("/images", StaticFiles(directory="Frontend/images"), name="images")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print(f"✅ RecruitIQ is running! Upload dir: {UPLOAD_DIR}")

@app.get("/kaithhealthcheck")
async def health_check():
    return {"status": "healthy"}

@app.get("/kaithheathcheck")
async def health_check_typo():
    return {"status": "healthy"}