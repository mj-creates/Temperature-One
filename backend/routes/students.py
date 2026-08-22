"""
Student Routes: Student profile listing and detailed inspection.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
import sqlite3

from backend.database.database import get_db_connection
from backend.database.crud import get_students, get_student_by_regno
from backend.domain_schemas import StudentSummary, StudentDetail

router = APIRouter(prefix="/api/students", tags=["Students"])


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


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
