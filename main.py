from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from Backend.app.core.database import create_db_and_tables
from Backend.app.api import auth, jobs, applications, pipeline, notification, analytics, interview
import os
import uvicorn

app = FastAPI(title="RecruitIQ API", description="AI-powered Applicant Tracking System", version="1.0.0",)

# CORS — allow frontend HTML files to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(pipeline.router)
app.include_router(notification.router)
app.include_router(analytics.router)
app.include_router(interview.router)

# ── Page Routes ──────────────────────────────────────────────────
@app.get("/")
def home():
    return FileResponse("frontend/home.html")

@app.get("/login")
def login():
    return FileResponse("frontend/index.html")

@app.get("/dashboard/recruiter")
def recruiter_dashboard():
    return FileResponse("frontend/dashboard/recruiter.html")

@app.get("/dashboard/candidate")
def candidate_dashboard():
    return FileResponse("frontend/dashboard/candidate.html")

@app.get("/jobs")
def jobs_page():
    return FileResponse("frontend/pages/jobs.html")

@app.get("/pipeline")
def pipeline_page():
    return FileResponse("frontend/pages/pipeline.html")

@app.get("/analytics")
def analytics_page():
    return FileResponse("frontend/pages/analytics.html")

@app.get("/interviews")
def interviews_page():
    return FileResponse("frontend/pages/interviews.html")

@app.get("/applications")
def applications_page():
    return FileResponse("frontend/pages/applications.html")

@app.get("/notifications")
def notifications_page():
    return FileResponse("frontend/pages/notifications.html")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)
