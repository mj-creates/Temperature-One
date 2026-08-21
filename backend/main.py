"""
Academic Advising & Prerequisite Conflict Resolver - FastAPI Backend Entrypoint
==============================================================================
Provides REST APIs for:
- Student Profile Management (/api/students)
- Curriculum Catalog & Degree Policy Rules (/api/subjects, /api/degree-requirements)
- Autonomous Multi-Agent Advising Orchestration (/api/agent)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.students import router as students_router
from backend.routes.subjects import router as subjects_router
from backend.routes.agents import router as agents_router

app = FastAPI(
    title="Academic Advising & Curriculum API",
    description=(
        "FastAPI backend for the Academic Advising & Prerequisite Conflict Resolver platform. "
        "Integrates SQLite database (university.db) with the autonomous multi-agent pipeline "
        "(Nexus Agent 01, Matrix Agent 02, Vector Agent 03, Background Check Agent 04)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS Configuration (Vite React Frontend on http://localhost:5173)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register API Routers
# ---------------------------------------------------------------------------
app.include_router(students_router)
app.include_router(subjects_router)
app.include_router(agents_router)


@app.get("/health", tags=["System Health"])
def health_check():
    """Health check endpoint for server and deployment monitoring."""
    return {
        "status": "ok",
        "service": "academic-advising-backend",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
def root():
    """Root entrypoint returning API metadata and documentation links."""
    return {
        "message": "Welcome to the Academic Advising & Prerequisite Conflict Resolver API",
        "documentation": "/docs",
        "health_check": "/health"
    }