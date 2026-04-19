from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from Backend.app.core.database import create_db_and_tables
from Backend.app.api import auth, jobs, applications, pipeline, notification, analytics, interview
import os
import uvicorn

app = FastAPI(
    title="RecruitIQ API",
    description="AI-powered Applicant Tracking System",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create upload dir ─────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)

# ── API Routers (must come BEFORE static mounts) ─────────────────
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(pipeline.router)
app.include_router(notification.router)
app.include_router(analytics.router)
app.include_router(interview.router)

# ── Static File Mounts ───────────────────────────────────────────
# FIX: Use "Frontend" (capital F) to match actual folder name on disk
# FIX: Mount CSS/JS/favicon/images so HTML pages can load them
app.mount("/uploads",   StaticFiles(directory="uploads"),            name="uploads")
app.mount("/css",       StaticFiles(directory="Frontend/css"),       name="css")
app.mount("/js",        StaticFiles(directory="Frontend/js"),        name="js")
app.mount("/favicon",   StaticFiles(directory="Frontend/favicon"),   name="favicon")
app.mount("/images",    StaticFiles(directory="Frontend/images"),    name="images")
app.mount("/pages",     StaticFiles(directory="Frontend/pages"),     name="pages")

# ── Page Routes ───────────────────────────────────────────────────
# FIX: All FileResponse paths use "Frontend/" (capital F)
@app.get("/")
def home():
    return FileResponse("Frontend/home.html")

@app.get("/login")
def login_page():
    return FileResponse("Frontend/index.html")

@app.get("/index.html")
def index_page():
    return FileResponse("Frontend/index.html")

@app.get("/dashboard/recruiter")
def recruiter_dashboard():
    return FileResponse("Frontend/dashboard/recruiter.html")

@app.get("/dashboard/candidate")
def candidate_dashboard():
    return FileResponse("Frontend/dashboard/candidate.html")

@app.get("/jobs")
def jobs_page():
    return FileResponse("Frontend/pages/jobs.html")

@app.get("/pipeline")
def pipeline_page():
    return FileResponse("Frontend/pages/pipeline.html")

@app.get("/analytics")
def analytics_page():
    return FileResponse("Frontend/pages/analytics.html")

@app.get("/interviews")
def interviews_page():
    return FileResponse("Frontend/pages/interviews.html")

@app.get("/applications")
def applications_page():
    return FileResponse("Frontend/pages/applications.html")

@app.get("/notifications")
def notifications_page():
    return FileResponse("Frontend/pages/notifications.html")

# ── Startup ───────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("✅ RecruitIQ is running!")

@app.get("/kaithhealthcheck")
async def health_check():
    return {"status": "healthy"}

@app.get("/kaithheathcheck")  # Their typo version too
async def health_check_typo():
    return {"status": "healthy"}