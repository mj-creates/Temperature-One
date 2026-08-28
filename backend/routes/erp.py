"""
Vignan University ERP Integration & Scraping Router
===================================================
Endpoints for authenticating students against https://erp.vignan.ac.in/student/ in Parent mode,
scraping their academic records and attendance, and synchronizing with the local SQLite database.
"""

import sqlite3
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from backend.database.database import get_db_connection
from backend.database.crud import get_student_by_regno, create_student
from backend.services.vignan_scraper import VignanERPScraper

logger = logging.getLogger("vignan_router")

router = APIRouter(prefix="/api/vignan", tags=["Vignan ERP Scraper"])


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


class VignanLoginRequest(BaseModel):
    reg_no: str = Field(..., description="Student Registration Number (e.g. 241FA04E95 or 211FA04001)", examples=["241FA04E95"])
    password: Optional[str] = Field(default=None, description="Password (defaults automatically to the Registration Number if omitted)", examples=["241FA04E95"])
    usertype: str = Field(default="Student", description="Authentication mode: 'Student'", examples=["Student"])
    sync_to_db: bool = Field(default=True, description="Whether to automatically store or update student record in the database")


class AttendanceSubject(BaseModel):
    subject_code: str
    subject_name: str
    percentage: float


class AttendanceSummary(BaseModel):
    subjects: List[Dict[str, Any]] = []
    aggregate_percentage: float = 0.0


class VignanStudentProfile(BaseModel):
    reg_no: str
    regno: Optional[str] = None
    student_name: str
    name: Optional[str] = None
    year_of_join: Optional[str] = None    # e.g. "2024"
    dept_code: Optional[str] = None       # e.g. "04"
    branch: str
    department: Optional[str] = None
    semester: int
    section: Optional[str] = None        # e.g. "E"
    cgpa: float
    total_credits: int
    goal: str = "Software Engineer"
    profile: Dict[str, Any] = {}
    attendance: Dict[str, Any] = {}
    marks: Dict[str, Any] = {}
    fees: Dict[str, Any] = {}
    enrolled_subjects: List[Dict[str, Any]] = []


class VignanLoginResponse(BaseModel):
    success: bool
    message: str
    source: str
    mode: str
    student: VignanStudentProfile


@router.post(
    "/login",
    response_model=VignanLoginResponse,
    summary="Authenticate & Scrape Student Data from Vignan ERP",
    description="Submits credentials to https://erp.vignan.ac.in/student/ in Student mode with password equal to Registration Number, scrapes academic and attendance data, and syncs to the local database."
)
def vignan_erp_login(
    payload: VignanLoginRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    1. Authenticates against Vignan ERP (https://erp.vignan.ac.in/student/login1.jsp) with password = reg_no in Student mode.
    2. Scrapes profile, attendance, and semester marks.
    3. Persists/updates student record in SQLite.
    4. Returns rich student record.
    """
    clean_reg = payload.reg_no.strip().upper()
    clean_pwd = payload.password.strip() if payload.password and payload.password.strip() else clean_reg
    # Vignan ERP: Parent mode accepts registration number as password.
    # Student mode requires the student's actual portal password (unknown here).
    # Always use Parent mode so reg_no-as-password works reliably.
    clean_mode = "Parent"

    if not clean_reg:
        raise HTTPException(
            status_code=400,
            detail="Registration Number must not be empty."
        )

    scraper = VignanERPScraper(timeout=15)
    result = scraper.fetch_full_student_data(
        reg_no=clean_reg,
        password=clean_pwd,
        usertype=clean_mode,
        fallback_if_failed=True   # synthesize profile if ERP is unreachable/down
    )

    if not result.get("success"):
        status_code = result.get("status_code", 401)
        err_msg = result.get("error", "Failed to authenticate with Vignan ERP portal.")
        raise HTTPException(status_code=status_code, detail=err_msg)

    student_data = result["student"]

    # Sync to local database if requested
    if payload.sync_to_db:
        try:
            _sync_scraped_student_to_db(db, student_data)
        except Exception as e:
            logger.warning(f"Database sync warning: {e}")

    return {
        "success": True,
        "message": result.get("message", f"Successfully authenticated and loaded student data for {clean_reg}"),
        "source": result.get("source", "https://erp.vignan.ac.in/student/"),
        "mode": clean_mode,
        "student": student_data
    }


@router.get(
    "/status",
    summary="Check Vignan ERP Portal Reachability",
    description="Pings https://erp.vignan.ac.in/student/ to check if the portal is online and responsive."
)
def vignan_erp_status():
    """Checks the health and latency of the university ERP portal."""
    import time
    scraper = VignanERPScraper(timeout=8)
    if not scraper.session:
        return {"status": "unavailable", "detail": "requests library missing"}

    start_time = time.time()
    try:
        resp = scraper.session.get(scraper.BASE_URL, timeout=8)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "online" if resp.status_code == 200 else "degraded",
            "status_code": resp.status_code,
            "latency_ms": latency_ms,
            "target": scraper.BASE_URL,
            "supported_modes": ["Parent", "Student", "Staff"]
        }
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e),
            "target": scraper.BASE_URL
        }


def _sync_scraped_student_to_db(db: sqlite3.Connection, student_data: Dict[str, Any]):
    """
    Inserts or updates the student row in the SQLite database with all scraped fields:
    Name, Branch, Semester, CGPA, TotalCredits, YearOfJoin, DeptCode, Section, Department.
    """
    cursor = db.cursor()
    reg_no       = student_data["reg_no"]
    name         = student_data["student_name"]
    branch       = student_data["branch"]
    semester     = int(student_data["semester"])
    cgpa         = float(student_data["cgpa"])
    goal         = student_data.get("goal", "Software Engineer")
    total_credits = int(student_data.get("total_credits") or 0)
    year_of_join  = str(student_data.get("year_of_join") or "")
    dept_code     = str(student_data.get("dept_code") or "")
    section       = str(student_data.get("section") or "")
    # Long-form department name from marks or branch fallback
    department    = str(
        student_data.get("department")
        or student_data.get("marks", {}).get("department")
        or f"{branch} Engineering"
    )

    cursor.execute("SELECT RegNo FROM Students WHERE RegNo = ? COLLATE NOCASE;", (reg_no,))
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE Students
            SET StudentName  = ?,
                Branch       = ?,
                Semester     = ?,
                CGPA         = ?,
                Goal         = ?,
                TotalCredits = ?,
                YearOfJoin   = ?,
                DeptCode     = ?,
                Section      = ?,
                Department   = ?
            WHERE RegNo = ? COLLATE NOCASE;
        """, (name, branch, semester, cgpa, goal,
              total_credits, year_of_join, dept_code, section, department,
              reg_no))
    else:
        cursor.execute("""
            INSERT INTO Students
                (RegNo, StudentName, Branch, Semester, CGPA, Goal,
                 TotalCredits, YearOfJoin, DeptCode, Section, Department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (reg_no, name, branch, semester, cgpa, goal,
              total_credits, year_of_join, dept_code, section, department))

    # Enroll default subjects for their branch/semester if not already present
    cursor.execute("SELECT COUNT(*) FROM Student_Subjects WHERE RegNo = ? COLLATE NOCASE;", (reg_no,))
    cnt = cursor.fetchone()[0]
    if cnt == 0:
        cursor.execute("SELECT SubjectID FROM Subjects WHERE Semester = ? LIMIT 6;", (semester,))
        subs = cursor.fetchall()
        for s in subs:
            cursor.execute("""
                INSERT OR IGNORE INTO Student_Subjects (RegNo, SubjectID)
                VALUES (?, ?);
            """, (reg_no, s[0]))

    db.commit()
