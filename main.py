from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from Backend.app.core.database import create_db_and_tables
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("Database is ready")

@app.get("/")
def home():
    return {"message": "RecruitIQ API is running 🚀",
        "docs": "/docs",
        "status": "ok"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)
