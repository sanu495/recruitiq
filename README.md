<div align="center">

<img src="https://img.shields.io/badge/RecruitIQ-AI--Powered%20ATS-8B5CF6?style=for-the-badge&logo=fastapi&logoColor=white" alt="RecruitIQ"/>

# 🤖 RecruitIQ — AI-Powered Applicant Tracking System

**A fully functional, production-deployed ATS built from scratch with FastAPI, Groq AI, and Vanilla JS.**

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-recruitiq--xu8u.onrender.com-22C55E?style=for-the-badge)](https://recruitiq-xu8u.onrender.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Groq AI](https://img.shields.io/badge/Groq-Llama%203-F55036?style=flat-square)](https://groq.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-ORM-8B5CF6?style=flat-square)](https://sqlmodel.tiangolo.com/)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://render.com/)

</div>

---

## 📌 About

**RecruitIQ** is a portfolio-grade, AI-powered Applicant Tracking System built entirely by a single developer. It solves a real problem: most small companies still manually read dozens of resumes to shortlist 3 candidates — slow, biased, and inefficient.

RecruitIQ uses **Groq's Llama 3** to automatically score every resume 0–100 against the job description the moment a candidate applies, giving recruiters an instant, AI-ranked shortlist. The platform covers the full hiring lifecycle — from job posting to offer — with no external SaaS dependency.

> **Built as a proof-of-concept portfolio project** demonstrating end-to-end backend architecture, AI integration, role-based access control, and production deployment.

---

## 🌐 Live Demo

**→ [https://recruitiq-xu8u.onrender.com/](https://recruitiq-xu8u.onrender.com/)**

| Role | Email | Password |
|------|-------|----------|
| Recruiter | Create your own account | — |
| Candidate | Create your own account | — |

> ℹ️ Hosted on Render Free tier — the server may take **~30 seconds to wake up** on first visit if idle.

---

## ✨ Features

### 🤖 AI Resume Screening
- Resume PDFs are parsed with `pdfplumber` the moment a candidate submits
- Groq's **Llama 3 (llama-3.1-8b-instant)** scores the resume 0–100 against the job description and required skills
- Returns: match score, strengths, skill gaps, recommendation label, and suggested interview questions
- Recruiters can also trigger manual re-screening from the Pipeline page

### 🔄 Visual Hiring Pipeline (Kanban Board)
- 6 stages: **Applied → Screening → Interview → Offer → Hired → Rejected**
- Move candidates between stages with one click
- Stage transitions automatically trigger candidate notifications
- Bulk-reject all "Applied" candidates at once
- Private recruiter notes per application

### 📊 Hiring Analytics Dashboard
- Pipeline breakdown bar chart
- Monthly application trend line chart
- AI score distribution histogram
- Applications-per-job horizontal bar chart
- Top AI-scored candidates table with CSV export

### 📅 Interview Scheduler
- Recruiters schedule interviews with date/time, duration, meeting link, and notes
- Candidates receive instant notifications and can confirm attendance
- Both sides see upcoming vs. all-history views with status filters

### 🔔 Smart Notifications
- Every stage change, interview schedule, and application event triggers a notification
- Unread badge on the bell icon
- Mark individual or all notifications as read / delete

### 🔐 Role-Based Access Control (RBAC)
- **Admin** — full access to all data across all recruiters
- **Recruiter** — manages own jobs, pipeline, interviews, analytics
- **Candidate** — applies to jobs, tracks application status, confirms interviews
- JWT authentication with bcrypt password hashing

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | FastAPI (Python 3.11) |
| **ORM** | SQLModel (built on SQLAlchemy + Pydantic) |
| **Database** | SQLite (dev/Render free) |
| **AI / LLM** | Groq API — Llama 3.1 8B Instant (free tier) |
| **PDF Parsing** | pdfplumber |
| **Authentication** | JWT (python-jose) + bcrypt (passlib) |
| **Frontend** | Vanilla JS + HTML/CSS (no React, no framework) |
| **Charts** | Chart.js 4 |
| **Deployment** | Render (Free Web Service) |
| **Static Serving** | FastAPI StaticFiles + FileResponse |

---

## 🗂️ Project Structure

```
RecruitIQ/
├── main.py                        # FastAPI app entry point, page routes, static mounts
├── Procfile                       # Render start command
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python 3.11.0
│
├── Backend/
│   └── app/
│       ├── api/
│       │   ├── auth.py            # Register, login, /me, admin user list
│       │   ├── jobs.py            # CRUD jobs, search/filter, auto-close expired
│       │   ├── applications.py    # Apply, withdraw, AI screening, notes, CSV export
│       │   ├── pipeline.py        # Stage transitions, kanban, bulk-reject
│       │   ├── interview.py       # Schedule, confirm, cancel, upcoming
│       │   ├── analytics.py       # Overview, pipeline, trends, AI scores, top candidates
│       │   └── notification.py    # List, read, mark-all-read, delete
│       ├── core/
│       │   ├── config.py          # Pydantic settings (env vars)
│       │   ├── database.py        # SQLAlchemy engine, session, create_tables
│       │   ├── security.py        # JWT encode/decode, password hash, require_role
│       │   └── genericdal.py      # Generic CRUD Data Access Layer
│       ├── Models/
│       │   └── models.py          # Pydantic request/response schemas
│       ├── Schema/
│       │   └── schema.py          # SQLModel table definitions + Enums
│       └── Services/
│           ├── ai_screening.py    # Groq API integration, screen_resume(), get_detailed_analysis()
│           └── pdf_parser.py      # pdfplumber text extraction + cleaning
│
└── Frontend/
    ├── home.html                  # Public landing page
    ├── index.html                 # Login / Register page
    ├── css/style.css              # Global dark theme design system
    ├── js/
    │   ├── api.js                 # All API calls (AuthAPI, JobsAPI, AppAPI, etc.)
    │   └── auth.js                # Route guard, sidebar, topbar, toast, helpers
    ├── dashboard/
    │   ├── recruiter.html         # Recruiter dashboard
    │   └── candidate.html         # Candidate dashboard
    └── pages/
        ├── jobs.html              # Job listing + post/edit + apply modal
        ├── pipeline.html          # Kanban board
        ├── analytics.html         # Charts and top candidates
        ├── interviews.html        # Interview schedule management
        ├── applications.html      # Candidate: my applications tracker
        └── notifications.html     # Notification center
```

---

## ⚙️ Architecture Highlights

### GenericDal Pattern
A reusable generic Data Access Layer (`genericdal.py`) handles all CRUD operations across every model — no repetitive boilerplate per table:
```python
dal = GenericDal(Application, session)
dal.create(app_obj)
dal.get(id)
dal.update(id, {"stage": "interview"})
dal.get_many_by_field("job_id", 3)
```

### Single-Origin Deployment
FastAPI serves **both the API and the entire frontend** from one URL. `StaticFiles` mounts handle CSS/JS/images, while explicit `@app.get()` routes serve each HTML page with `FileResponse`. `api.js` uses `BASE_URL = ''` (empty string) so all fetch calls are same-origin — no CORS complexity, no separate frontend server needed.

### AI Screening Flow
```
Candidate submits resume PDF
        ↓
pdfplumber extracts raw text
        ↓
resume_text + job_description + required_skills → Groq API (Llama 3)
        ↓
Returns JSON: { score, strengths, gaps, recommendation, feedback }
        ↓
Stored in Application.ai_score + Application.ai_feedback
        ↓
Visible in Pipeline card, Analytics table, Candidate dashboard
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sanu495/recruitiq.git
cd recruitiq

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run the app
uvicorn main:app --reload

# 6. Open in browser
# http://localhost:8000
```

### Environment Variables

```env
DATABASE_URL=sqlite:///./recruitiq.db   # Default for local dev
SECRET_KEY=your_secret_key_here
GROQ_API_KEY=your_groq_api_key_here     # Free at https://console.groq.com
```

> Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card needed.

---

## 📡 API Reference

The full interactive API docs are available at:
**[https://recruitiq-xu8u.onrender.com/docs](https://recruitiq-xu8u.onrender.com/docs)**

### Key Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/auth/register` | Create account | Public |
| `POST` | `/api/auth/login` | Login → JWT | Public |
| `GET` | `/api/auth/me` | Current user info | Any |
| `GET` | `/api/jobs` | List jobs (search, filter) | Any |
| `POST` | `/api/jobs` | Post a new job | Recruiter |
| `POST` | `/api/applications` | Apply with resume PDF | Candidate |
| `GET` | `/api/applications/my` | My applications | Candidate |
| `POST` | `/api/applications/{id}/screen` | Trigger AI screening | Recruiter |
| `GET` | `/api/applications/{id}/analysis` | Detailed AI analysis | Recruiter |
| `PATCH` | `/api/pipeline/{app_id}/stage` | Move candidate stage | Recruiter |
| `GET` | `/api/analytics/overview` | Dashboard stats | Recruiter |
| `POST` | `/api/interviews` | Schedule interview | Recruiter |
| `PATCH` | `/api/interviews/{id}/confirm` | Confirm interview | Candidate |
| `GET` | `/api/notifications` | My notifications | Any |

---

## 🎯 Key Design Decisions

| Decision | Reason |
|----------|--------|
| **No React / no framework** | Demonstrated raw JS capability; keeps deployment simple (no build step) |
| **SQLModel over raw SQLAlchemy** | Combines Pydantic validation + ORM in one model definition |
| **int IDs instead of UUIDs** | Simpler queries, better readability for a portfolio project |
| **Groq over OpenAI** | Free tier, faster inference (Llama 3), no rate limits for demo use |
| **GenericDal pattern** | Eliminates repetitive CRUD code; single place to maintain query logic |
| **Single-file deployment** | FastAPI serves frontend + API from one server, one URL, zero DevOps overhead |
| **SQLite on Render Free** | No persistent disk needed for portfolio demos; easy to swap for MySQL via `DATABASE_URL` env var |

---

## 📸 Pages Overview

| Page | Role | Description |
|------|------|-------------|
| `/` | Public | Landing page with features, AI demo, builder profile |
| `/login` | Public | Login + Register with role selection |
| `/dashboard/recruiter` | Recruiter | Stats, recent applications, pipeline donut chart, upcoming interviews |
| `/dashboard/candidate` | Candidate | Applications tracker, upcoming interviews, notifications |
| `/jobs` | Both | Browse + filter jobs (candidate) / Post + manage jobs (recruiter) |
| `/pipeline` | Recruiter | Kanban board grouped by stage, candidate detail modal, AI screening |
| `/analytics` | Recruiter | 4 charts + top candidates table + CSV export |
| `/interviews` | Both | Schedule (recruiter) / Confirm (candidate) interview sessions |
| `/applications` | Candidate | Full application history with stage progress bar |
| `/notifications` | Both | Notification center with read/delete |

---

## 👤 Built By

**Sanoop A** — Python / FastAPI Backend Developer

[![Portfolio](https://img.shields.io/badge/Portfolio-sanoop--developer.vercel.app-8B5CF6?style=flat-square&logo=vercel&logoColor=white)](https://sanoop-developer.vercel.app/)
[![GitHub](https://img.shields.io/badge/GitHub-sanu495-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/sanu495)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-sanoop--sanu658-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/sanoop-sanu658/)
[![Email](https://img.shields.io/badge/Email-sanoops658@gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:sanoops658@gmail.com)

B.Sc. Computer Science — Manonmaniam Sundaranar University, 2024  
Available for entry-level Python / FastAPI backend roles at Technopark, Trivandrum.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**⭐ Star this repo if you found it useful!**

*Built with FastAPI + Groq AI + ❤️*

</div>