from fastapi import FastAPI
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
    allow_credentials=True,
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

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)
