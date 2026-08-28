"""
Academic Advising & Prerequisite Conflict Resolver - FastAPI Backend Entrypoint
==============================================================================
Provides REST APIs for:
- Student Profile Management (/api/students)
- Curriculum Catalog & Degree Policy Rules (/api/subjects, /api/degree-requirements)
- Curriculum Knowledge Graph (/api/graph)
- Autonomous Multi-Agent Advising Orchestration (/api/agent, /api/advising)
- Graph-RAG Policy & Citation Retrieval (/api/rag, /api/policies)
- Formal Constraint & Conflict Diagnostics (/api/analysis, /api/conflicts)
- Course Substitutions & Equivalences (/api/v1/substitutes, /api/substitutions)
- Faculty Waivers & Overrides (/api/waivers, /api/faculty)
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import sqlite3

from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root and agent_core to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_CORE_DIR = PROJECT_ROOT / "agent_core"
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(AGENT_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_CORE_DIR))

try:
    from backend.database.database import get_db_connection, DB_PATH
except ImportError:
    from database.database import get_db_connection, DB_PATH

# Import Modular Routers from upstream
from backend.routes.students import router as students_router
from backend.routes.subjects import router as subjects_router
from backend.routes.agents import router as agents_router
from backend.routes.graph import router as graph_router
from backend.routes.analysis import router as analysis_router
from backend.routes.waivers import router as waivers_router
from backend.routes.rag import router as rag_router
from backend.routes.substitutes import router as substitutes_router
from backend.routes.orchestrator import router as orchestrator_router
from backend.routes.teacher import router as teacher_router
from backend.routes.external_courses import router as external_courses_router
from backend.routes.counseling import router as counseling_router
from backend.routes.erp import router as erp_router

# Import Agent Core modules
try:
    from agent_core.agent_schemas import (
        StudentState,
        MatrixPathResponse,
        ConflictDiagnosticReport,
        MomentumPlan,
        GraphRAGQueryResult,
        FacultyPetitionRecord,
        FacultyPetitionCreate,
        FacultyActionPayload,
        AdvisingSessionResponse,
    )
    from agent_core.agent_4_background_check import Agent4BackgroundCheck
    from agent_core.agent_matrix import MatrixAgent
    from agent_core.agent_3_vector import Agent3Vector
    from agent_core.agent_5_codex import CodexGraphRAGAgent
    from agent_core.agent_sentinel_verifier import SentinelVerifierAgent
    from agent_core.nexus import NexusAgent
except ImportError:
    try:
        from schemas import (
            StudentState,
            MatrixPathResponse,
            ConflictDiagnosticReport,
            MomentumPlan,
            GraphRAGQueryResult,
            FacultyPetitionRecord,
            FacultyPetitionCreate,
            FacultyActionPayload,
            AdvisingSessionResponse,
        )
        from agent_4_background_check import Agent4BackgroundCheck
        from agent_matrix import MatrixAgent
        from agent_3_vector import Agent3Vector
        from agent_codex_rag import CodexGraphRAGAgent
        from agent_sentinel_verifier import SentinelVerifierAgent
        from nexus import NexusAgent
    except Exception:
        pass


app = FastAPI(
    title="Omega — Academic Pathway Intelligence API",
    description=(
        "FastAPI backend for the Academic Advising & Prerequisite Conflict Resolver platform. "
        "Integrates SQLite database (university.db) with the autonomous multi-agent pipeline "
        "(Nexus Agent 01, Matrix Agent 02, Vector Agent 03, Background Check Agent 04, Codex Agent 05, Sentinel Agent 06)."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
import os as _os

_FRONTEND_URL = _os.getenv("FRONTEND_URL", "https://omega-nine-tau.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://omega-nine-tau.vercel.app",   # deployed Vercel frontend
        _FRONTEND_URL,                          # override via env var if needed
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
app.include_router(graph_router)
app.include_router(analysis_router)
app.include_router(waivers_router)
app.include_router(rag_router)
app.include_router(orchestrator_router)
app.include_router(erp_router)
app.include_router(substitutes_router, prefix="/api/v1/substitutes", tags=["Substitutes"])
app.include_router(teacher_router)
app.include_router(external_courses_router)
app.include_router(counseling_router)

# Initialize Agent Singleton Instances
nexus_agent = NexusAgent(db_path=DB_PATH)
state_agent = Agent4BackgroundCheck(db_path=DB_PATH)
matrix_agent = MatrixAgent(db_path=DB_PATH)
vector_agent = Agent3Vector()
codex_agent = CodexGraphRAGAgent(db_path=DB_PATH)
sentinel_agent = SentinelVerifierAgent(db_path=DB_PATH)


# ===========================================================================
# 1. SYSTEM HEALTH & METADATA
# ===========================================================================
@app.get("/health", tags=["System Health"])
@app.get("/api/health", tags=["System Health"])
def health_check():
    """Health check endpoint for server and deployment monitoring."""
    db_exists = DB_PATH.exists()
    return {
        "status": "healthy" if db_exists else "degraded",
        "service": "Omega Academic Pathway Intelligence",
        "version": "2.0.0",
        "database_connected": db_exists,
        "active_agents": ["Nexus (Agent 01)", "The Matrix (Agent 02)", "Vector (Agent 03)", "State (Agent 04)", "Codex Graph-RAG (Agent 05)", "Sentinel (Agent 06)"]
    }


@app.get("/", tags=["Root"])
def root():
    """Root entrypoint returning API metadata and documentation links."""
    return {
        "message": "Welcome to the Academic Advising & Prerequisite Conflict Resolver API",
        "documentation": "/docs",
        "health_check": "/health"
    }


# ===========================================================================
# 2. MULTI-AGENT ADVISING PIPELINE & CHAT ENDPOINTS
# ===========================================================================
class AdvisingRequest(BaseModel):
    student_id: str
    career_goal: Optional[str] = None


@app.post("/api/advising/pipeline", response_model=AdvisingSessionResponse, tags=["Advising Engine"])
def run_advising_pipeline(payload: AdvisingRequest):
    """
    Triggers the complete decentralized multi-agent advising session:
    Nexus -> State Synthesizer -> The Matrix -> Sentinel -> Codex Graph-RAG -> Vector.
    """
    try:
        session_result = nexus_agent.run_full_advising_pipeline(
            student_id=payload.student_id,
            custom_goal=payload.career_goal
        )
        return session_result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advising pipeline error: {e}")


class ChatMessagePayload(BaseModel):
    student_id: str
    message: str


@app.post("/api/advising/chat", tags=["Advising Engine"])
def advising_chat(payload: ChatMessagePayload):
    """
    Interactive natural-language academic advising with citation-traceable reasoning.
    """
    try:
        reply_data = nexus_agent.process_chat_message(
            student_id=payload.student_id,
            message=payload.message
        )
        return reply_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e}")


# ===========================================================================
# 3. CONFLICT RESOLVER & FORMAL CONSTRAINT DIAGNOSTICS
# ===========================================================================
class ConflictCheckRequest(BaseModel):
    student_id: str


@app.post("/api/conflicts/check", response_model=ConflictDiagnosticReport, tags=["Conflict Diagnostics"])
def check_student_conflicts(payload: ConflictCheckRequest):
    """
    Runs formal constraint verification to identify missing prerequisites, credit overloads,
    corequisite mismatches, and graduation risks.
    """
    raw_record, err = state_agent.fetch_raw_student_from_db(payload.student_id)
    if err or not raw_record:
        raise HTTPException(status_code=404, detail=f"Student '{payload.student_id}' not found.")

    enrolled_ids = [s["SubjectID"] for s in raw_record.get("enrolled_subjects", [])]
    completed_ids = enrolled_ids[:]

    report = sentinel_agent.evaluate_student_conflicts_and_risks(
        student_id=payload.student_id,
        student_profile={
            "cgpa": float(raw_record.get("current_gpa", 7.5)),
            "semester": int(raw_record.get("semester", 1)),
            "career_goal": raw_record.get("career_goal", "Computer Science")
        },
        enrolled_subject_ids=enrolled_ids,
        completed_subject_ids=completed_ids
    )
    return report


# ===========================================================================
# 4. DEGREE PATHWAY GENERATION & COURSE SUBSTITUTIONS
# ===========================================================================
class PathwayRequest(BaseModel):
    student_id: str
    target_node: Optional[str] = None
    career_goal: Optional[str] = None


@app.post("/api/pathway/generate", response_model=MatrixPathResponse, tags=["Degree Pathways"])
def generate_student_pathway(payload: PathwayRequest):
    """
    Generates a personalized, chronological semester progression pathway to target course or graduation.
    """
    raw_record, err = state_agent.fetch_raw_student_from_db(payload.student_id)
    if err or not raw_record:
        raise HTTPException(status_code=404, detail=f"Student '{payload.student_id}' not found.")

    enrolled_ids = [s["SubjectID"] for s in raw_record.get("enrolled_subjects", [])]
    sem = int(raw_record.get("semester", 1))
    cgpa = float(raw_record.get("current_gpa", 7.5))
    goal = payload.career_goal or raw_record.get("career_goal", "Software Engineering")

    max_credits = 24.0 if cgpa >= 8.0 else (16.0 if cgpa < 6.0 else 20.0)

    if payload.target_node:
        path_json = matrix_agent.compute_path(
            student_id=payload.student_id,
            target_node=payload.target_node,
            completed_nodes=enrolled_ids,
            max_credits_per_step=max_credits
        )
        return MatrixPathResponse.model_validate_json(path_json)
    else:
        pathway = matrix_agent.generate_degree_progression_pathway(
            student_id=payload.student_id,
            current_semester=sem,
            completed_nodes=enrolled_ids,
            career_goal=goal,
            max_credits_per_semester=max_credits
        )
        return pathway


@app.get("/api/substitutions/{subject_id}", tags=["Course Substitutions"])
def get_course_substitutions(subject_id: str):
    """Retrieves approved course substitutions and equivalent elective tracks."""
    substitutions = matrix_agent.get_course_substitutions(subject_id)
    return {
        "subject_id": subject_id,
        "count": len(substitutions),
        "substitutions": substitutions
    }


# ===========================================================================
# 5. GRAPH-RAG POLICY KNOWLEDGE BASE
# ===========================================================================
@app.get("/api/policies/search", tags=["Policy Graph-RAG"])
def search_policies(
    query: Optional[str] = Query(None, description="Search query keywords"),
    category: Optional[str] = Query(None, description="Policy category filter")
):
    """Searches the Academic Policies Graph-RAG Knowledge Base."""
    policies = codex_agent.fetch_all_policies()
    if category:
        policies = [p for p in policies if p["Category"].lower() == category.lower()]
    if query:
        citations = codex_agent.retrieve_policies_for_query(query, top_k=5)
        return {
            "query": query,
            "count": len(citations),
            "citations": citations
        }
    return {
        "count": len(policies),
        "policies": policies
    }


# ===========================================================================
# 6. FACULTY OVERRIDE & PETITION PORTAL
# ===========================================================================
@app.get("/api/faculty/petitions", tags=["Faculty Portal"])
def list_faculty_petitions(
    reg_no: Optional[str] = Query(None, description="Filter petitions by RegNo"),
    status: Optional[str] = Query(None, description="Filter petitions by status (PENDING, APPROVED, REJECTED)")
):
    """Lists all faculty waiver, overload, and substitution petitions."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            fp.PetitionID, fp.RegNo, st.StudentName,
            fp.SubjectID, sb.SubjectName,
            fp.PetitionType, fp.Reason, fp.Status,
            fp.FacultyRemarks, fp.Timestamp, fp.AuditHash
        FROM Faculty_Petitions fp
        LEFT JOIN Students st ON fp.RegNo = st.RegNo
        LEFT JOIN Subjects sb ON fp.SubjectID = sb.SubjectID
        WHERE 1=1
    """
    params = []
    if reg_no:
        query += " AND fp.RegNo = ?"
        params.append(reg_no)
    if status:
        query += " AND fp.Status = ?"
        params.append(status.upper())

    query += " ORDER BY fp.Timestamp DESC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    return {
        "count": len(records),
        "petitions": records
    }


@app.post("/api/faculty/petitions", response_model=FacultyPetitionRecord, tags=["Faculty Portal"])
def create_faculty_petition(payload: FacultyPetitionCreate):
    """Submits a new student petition for prerequisite waiver, credit overload, or substitution."""
    try:
        record = sentinel_agent.create_petition(payload)
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit faculty petition: {e}")


@app.post("/api/faculty/petitions/{petition_id}/action", response_model=FacultyPetitionRecord, tags=["Faculty Portal"])
def action_faculty_petition(petition_id: str, payload: FacultyActionPayload):
    """Approves or rejects a faculty petition with formal remarks and cryptographic audit log."""
    updated_record = sentinel_agent.process_faculty_action(
        petition_id=petition_id,
        action=payload.action,
        remarks=payload.faculty_remarks
    )
    if not updated_record:
        raise HTTPException(status_code=404, detail=f"Petition '{petition_id}' was not found.")
    return updated_record


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
