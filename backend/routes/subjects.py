"""
Catalog & Degree Policy Routes: Course catalog grouped by semester and degree rules.
"""

from collections import defaultdict
from fastapi import APIRouter, HTTPException, Depends
import sqlite3

from backend.database.database import get_db_connection
from backend.database.crud import get_all_subjects, get_degree_requirements
from backend.schemas import SubjectsBySemesterResponse, DegreeRequirementsResponse, SubjectItem

router = APIRouter(prefix="/api", tags=["Curriculum & Degree Requirements"])


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@router.get(
    "/subjects",
    response_model=SubjectsBySemesterResponse,
    summary="Get course catalog",
    description="Retrieve all 60 catalog subjects grouped by semester level (Semester 1 to Semester 4)."
)
def get_catalog_subjects(db: sqlite3.Connection = Depends(get_db)):
    """Fetches all catalog subjects grouped by semester."""
    try:
        raw_subjects = get_all_subjects(db)
        semesters_dict = defaultdict(list)

        for sub in raw_subjects:
            sem_key = f"Semester {sub['semester']}"
            semesters_dict[sem_key].append(SubjectItem(**sub))

        all_subject_items = [SubjectItem(**sub) for sub in raw_subjects]

        return SubjectsBySemesterResponse(
            total_subjects=len(raw_subjects),
            semesters=dict(semesters_dict),
            all_subjects=all_subject_items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subjects catalog: {str(e)}")


@router.get(
    "/degree-requirements",
    response_model=DegreeRequirementsResponse,
    summary="Get degree policy and graduation rules",
    description="Retrieve curriculum rules including the 160 total credits requirement and semester targets."
)
def get_degree_policy(db: sqlite3.Connection = Depends(get_db)):
    """Returns degree requirements and graduation constraints from the database."""
    try:
        return get_degree_requirements(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch degree requirements: {str(e)}")
