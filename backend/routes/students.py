"""
Student Routes: Student profile listing, inspection, and account creation.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel, Field
import sqlite3

from backend.database.database import get_db_connection
from backend.database.crud import get_students, get_student_by_regno, create_student
from backend.domain_schemas import StudentSummary, StudentDetail

router = APIRouter(prefix="/api/students", tags=["Students"])


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


class StudentCreatePayload(BaseModel):
    reg_no: str = Field(..., description="Unique Registration ID, e.g. REG2001", examples=["REG2001"])
    student_name: str = Field(..., description="Full name of student", examples=["Saketh Rao"])
    semester: int = Field(default=1, ge=1, le=8, description="Enrolled semester (1 to 8)")
    cgpa: float = Field(default=8.0, ge=0.0, le=10.0, description="Starting or current CGPA")
    goal: str = Field(default="AI Researcher", description="Selected career specialization")
    enrolled_subject_ids: Optional[List[str]] = Field(default=None, description="Optional custom subject enrollments")


@router.get(
    "",
    response_model=List[StudentSummary],
    summary="List all students",
    description="Retrieve student records with optional semester and career goal filtering."
)
def list_students(
    semester: Optional[int] = Query(
        None,
        ge=1,
        le=8,
        description="Filter students by current semester (1 to 4)"
    ),
    goal: Optional[str] = Query(
        None,
        description="Filter students by matching career goal (e.g., 'Data Scientist', 'AI Researcher')"
    ),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns a list of student summaries matching filter criteria."""
    try:
        return get_students(db, semester=semester, goal=goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.post(
    "",
    response_model=StudentDetail,
    summary="Create a new student enrollment account",
    description="Registers a new student profile, assigns career goals, and enrolls in initial semester subjects."
)
def register_student(
    payload: StudentCreatePayload,
    db: sqlite3.Connection = Depends(get_db)
):
    """Creates a new student account in DBMS."""
    existing = get_student_by_regno(db, reg_no=payload.reg_no)
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{payload.reg_no}' already exists in the system.")

    try:
        new_record = create_student(
            db,
            reg_no=payload.reg_no,
            student_name=payload.student_name,
            semester=payload.semester,
            cgpa=payload.cgpa,
            goal=payload.goal,
            enrolled_subject_ids=payload.enrolled_subject_ids
        )
        return new_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create student account: {str(e)}")


@router.get(
    "/{reg_no}",
    response_model=StudentDetail,
    summary="Get single student details",
    description="Retrieve a single student's profile along with their 6 enrolled subjects and total credits."
)
def get_single_student(
    reg_no: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """Fetches full student details, enrolled subjects, and credit sums by registration number."""
    student = get_student_by_regno(db, reg_no=reg_no)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with Registration Number '{reg_no}' not found in the database."
        )
    return student
