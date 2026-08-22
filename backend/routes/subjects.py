"""
Catalog, Degree Policy & Prerequisite Conflict Resolver Routes
==============================================================
Provides REST APIs for:
- Course Catalog grouped by semester (/api/subjects)
- University Degree Policy (/api/degree-requirements)
- Prerequisite & Credit Conflict Detection Engine (/api/curriculum/conflict-check)
"""

from collections import defaultdict
from typing import List, Dict, Any, Set, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import sqlite3

from backend.database.database import get_db_connection
from backend.database.crud import get_all_subjects, get_degree_requirements
from backend.domain_schemas import (
    SubjectsBySemesterResponse,
    DegreeRequirementsResponse,
    SubjectItem,
    ConflictCheckRequest,
    ConflictCheckResponse,
)

router = APIRouter(prefix="/api", tags=["Curriculum & Degree Requirements"])


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Curriculum Rulebook: Prerequisite, Co-requisite, and Anti-requisite Mappings
# ---------------------------------------------------------------------------
# Maps subject IDs to their structural graph constraints for conflict resolution
CURRICULUM_RULES: Dict[str, Dict[str, Any]] = {
    # Semester 1
    "Sub_1_1": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_2": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_3": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_4": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_5": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_6": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_7": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_8": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_9": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_10": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_11": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_12": {"prereqs": [], "coreqs": ["Sub_1_7"], "antireqs": []}, # Hardware Lab co-requisite with Digital Logic
    "Sub_1_13": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_14": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_15": {"prereqs": [], "coreqs": [], "antireqs": []},

    # Semester 2
    "Sub_2_1": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []}, # DSA requires Intro to Programming
    "Sub_2_2": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []}, # OOP Java requires Intro to Programming
    "Sub_2_3": {"prereqs": ["Sub_1_2"], "coreqs": [], "antireqs": []}, # Linear Algebra requires Calculus
    "Sub_2_4": {"prereqs": ["Sub_1_7"], "coreqs": [], "antireqs": []}, # Comp Arch requires Digital Logic
    "Sub_2_5": {"prereqs": ["Sub_1_2"], "coreqs": [], "antireqs": []}, # Prob & Stats requires Calculus
    "Sub_2_6": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_7": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []}, # Software Eng requires Programming
    "Sub_2_8": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_9": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []}, # Relational DB requires Programming
    "Sub_2_10": {"prereqs": ["Sub_1_10"], "coreqs": [], "antireqs": []}, # Automata requires Discrete Math
    "Sub_2_11": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_12": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_13": {"prereqs": ["Sub_1_12"], "coreqs": [], "antireqs": []}, # Linux Shell requires Hardware Lab
    "Sub_2_14": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_15": {"prereqs": [], "coreqs": [], "antireqs": []},

    # Semester 3
    "Sub_3_1": {"prereqs": ["Sub_2_9"], "coreqs": [], "antireqs": []}, # DBMS requires Relational DB Concepts
    "Sub_3_2": {"prereqs": ["Sub_2_4", "Sub_2_13"], "coreqs": [], "antireqs": []}, # OS requires Comp Arch & Linux
    "Sub_3_3": {"prereqs": ["Sub_2_1"], "coreqs": [], "antireqs": []}, # Algorithms requires DSA
    "Sub_3_4": {"prereqs": ["Sub_3_2"], "coreqs": [], "antireqs": []}, # Networks requires OS
    "Sub_3_5": {"prereqs": ["Sub_2_3", "Sub_2_5"], "coreqs": [], "antireqs": []}, # AI requires Linear Algebra & Prob/Stats
    "Sub_3_6": {"prereqs": ["Sub_2_6"], "coreqs": ["Sub_3_1"], "antireqs": []}, # Full Stack co-requisite with DBMS
    "Sub_3_7": {"prereqs": ["Sub_2_2"], "coreqs": [], "antireqs": []}, # Mobile App requires Java OOP
    "Sub_3_8": {"prereqs": ["Sub_1_10"], "coreqs": [], "antireqs": []}, # Cryptography requires Discrete Math
    "Sub_3_9": {"prereqs": ["Sub_2_4"], "coreqs": [], "antireqs": []}, # Cloud Computing requires Comp Arch
    "Sub_3_10": {"prereqs": ["Sub_2_10"], "coreqs": [], "antireqs": []}, # Compiler Design requires Automata
    "Sub_3_11": {"prereqs": ["Sub_2_9"], "coreqs": [], "antireqs": []}, # Data Warehousing requires Relational DB
    "Sub_3_12": {"prereqs": ["Sub_2_1"], "coreqs": [], "antireqs": []}, # Distributed Systems requires DSA
    "Sub_3_13": {"prereqs": ["Sub_2_13"], "coreqs": [], "antireqs": []}, # Cyber Forensics requires Linux
    "Sub_3_14": {"prereqs": ["Sub_1_13"], "coreqs": [], "antireqs": []}, # NLP Basics requires Python Prototyping
    "Sub_3_15": {"prereqs": ["Sub_2_7"], "coreqs": [], "antireqs": []}, # Agile & DevOps requires Software Eng

    # Semester 4
    "Sub_4_1": {"prereqs": ["Sub_3_3", "Sub_3_5"], "coreqs": [], "antireqs": []}, # ML Systems requires Algorithms & AI
    "Sub_4_2": {"prereqs": ["Sub_4_1"], "coreqs": [], "antireqs": []}, # Deep Learning requires ML Systems
    "Sub_4_3": {"prereqs": ["Sub_3_1", "Sub_2_5"], "coreqs": [], "antireqs": []}, # Big Data requires DBMS & Stats
    "Sub_4_4": {"prereqs": ["Sub_3_15", "Sub_3_4"], "coreqs": [], "antireqs": []}, # DevOps & CI/CD requires Agile & Networks
    "Sub_4_5": {"prereqs": ["Sub_3_8"], "coreqs": [], "antireqs": []}, # InfoSec requires Cryptography
    "Sub_4_6": {"prereqs": ["Sub_3_4"], "coreqs": [], "antireqs": ["Sub_4_13"]}, # IoT vs Quantum Computing antirequisite
    "Sub_4_7": {"prereqs": ["Sub_3_5", "Sub_2_3"], "coreqs": [], "antireqs": []}, # Computer Vision requires AI & Linear Algebra
    "Sub_4_8": {"prereqs": ["Sub_3_8", "Sub_3_12"], "coreqs": [], "antireqs": []}, # Blockchain requires Crypto & Dist Systems
    "Sub_4_9": {"prereqs": ["Sub_3_9", "Sub_3_6"], "coreqs": [], "antireqs": []}, # Cloud Microservices requires Cloud & Full Stack
    "Sub_4_10": {"prereqs": ["Sub_3_2"], "coreqs": [], "antireqs": []}, # Parallel Computing requires OS
    "Sub_4_11": {"prereqs": ["Sub_4_1"], "coreqs": [], "antireqs": []}, # Reinforcement Learning requires ML Systems
    "Sub_4_12": {"prereqs": ["Sub_2_7"], "coreqs": [], "antireqs": []}, # QA & Testing requires Software Eng
    "Sub_4_13": {"prereqs": ["Sub_2_3"], "coreqs": [], "antireqs": ["Sub_4_6"]}, # Quantum Computing vs IoT
    "Sub_4_14": {"prereqs": ["Sub_3_11"], "coreqs": [], "antireqs": []}, # Data Visualization requires Data Warehousing
    "Sub_4_15": {"prereqs": ["Sub_3_3", "Sub_3_1"], "coreqs": [], "antireqs": []}, # Capstone requires Algorithms & DBMS
}


# ---------------------------------------------------------------------------
# 1. Prerequisite & Credit Conflict Detection Engine
# ---------------------------------------------------------------------------
@router.post(
    "/curriculum/conflict-check",
    response_model=ConflictCheckResponse,
    summary="Validate proposed 6-course schedule for conflicts",
    description="Performs the 4 formal checks: Prerequisites, Co-requisites, Anti-requisites, and Credit Range [12, 24]."
)
def check_course_conflicts(
    request: ConflictCheckRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Evaluates a proposed schedule of 6 courses against:
    1. Prerequisites: Must already be completed by student.
    2. Co-requisites: Must be taken concurrently in proposed list or already completed.
    3. Anti-requisites: Mutually exclusive courses cannot be taken together or repeated.
    4. Credit Load: Total sum of credits must fall within [12, 24] credits.
    """
    cursor = db.cursor()

    # Step 1: Verify student existence in database
    cursor.execute(
        "SELECT RegNo, StudentName, Semester, CGPA FROM Students WHERE RegNo = ? COLLATE NOCASE;",
        (request.reg_no.strip(),)
    )
    student_row = cursor.fetchone()
    if not student_row:
        raise HTTPException(
            status_code=404,
            detail=f"Student with Registration Number '{request.reg_no}' not found in database."
        )

    # Step 2: Query student's already completed / registered subjects
    cursor.execute(
        "SELECT SubjectID FROM Student_Subjects WHERE RegNo = ? COLLATE NOCASE;",
        (request.reg_no.strip(),)
    )
    completed_rows = cursor.fetchall()
    completed_courses: Set[str] = {row["SubjectID"] for row in completed_rows if row and row["SubjectID"]}

    # Step 3: Fetch course metadata (names and credits) from Subjects catalog
    proposed_set: Set[str] = set(request.proposed_courses)
    conflicts: List[str] = []

    cursor.execute("SELECT SubjectID, SubjectName, Credits, Semester FROM Subjects;")
    catalog_rows = cursor.fetchall()
    catalog_map: Dict[str, Dict[str, Any]] = {
        r["SubjectID"]: {
            "name": r["SubjectName"],
            "credits": int(r["Credits"]),
            "semester": int(r["Semester"])
        }
        for r in catalog_rows
    }

    # Verify all proposed course IDs exist in the catalog
    total_credits = 0
    for course_id in request.proposed_courses:
        if course_id not in catalog_map:
            conflicts.append(f"Invalid Course Error: '{course_id}' does not exist in the university catalog.")
            total_credits += 3  # Fallback assumption for credit summing
        else:
            total_credits += catalog_map[course_id]["credits"]

    # -----------------------------------------------------------------------
    # CHECK 1: Prerequisites Check
    # -----------------------------------------------------------------------
    for course_id in request.proposed_courses:
        rules = CURRICULUM_RULES.get(course_id, {})
        prereqs = rules.get("prereqs", [])
        for prereq in prereqs:
            if prereq not in completed_courses:
                prereq_name = catalog_map.get(prereq, {}).get("name", prereq)
                target_name = catalog_map.get(course_id, {}).get("name", course_id)
                conflicts.append(
                    f"Prerequisite conflict: '{target_name}' ({course_id}) requires '{prereq_name}' ({prereq}) "
                    f"to be completed prior to enrollment."
                )

    # -----------------------------------------------------------------------
    # CHECK 2: Co-requisites Check (Concurrent or Previously Completed)
    # -----------------------------------------------------------------------
    for course_id in request.proposed_courses:
        rules = CURRICULUM_RULES.get(course_id, {})
        coreqs = rules.get("coreqs", [])
        for coreq in coreqs:
            if coreq not in proposed_set and coreq not in completed_courses:
                coreq_name = catalog_map.get(coreq, {}).get("name", coreq)
                target_name = catalog_map.get(course_id, {}).get("name", course_id)
                conflicts.append(
                    f"Co-requisite conflict: '{target_name}' ({course_id}) requires co-requisite course "
                    f"'{coreq_name}' ({coreq}) to be enrolled concurrently in the same semester."
                )

    # -----------------------------------------------------------------------
    # CHECK 3: Anti-requisites Check (Mutually Exclusive Courses)
    # -----------------------------------------------------------------------
    seen_antireq_pairs: Set[tuple] = set()
    for course_id in request.proposed_courses:
        rules = CURRICULUM_RULES.get(course_id, {})
        antireqs = rules.get("antireqs", [])
        for antireq in antireqs:
            pair = tuple(sorted([course_id, antireq]))
            if antireq in proposed_set:
                if pair not in seen_antireq_pairs:
                    seen_antireq_pairs.add(pair)
                    target_name = catalog_map.get(course_id, {}).get("name", course_id)
                    anti_name = catalog_map.get(antireq, {}).get("name", antireq)
                    conflicts.append(
                        f"Anti-requisite conflict: '{target_name}' ({course_id}) and '{anti_name}' ({antireq}) "
                        f"are mutually exclusive and cannot be taken together in the same semester."
                    )
            elif antireq in completed_courses:
                if pair not in seen_antireq_pairs:
                    seen_antireq_pairs.add(pair)
                    target_name = catalog_map.get(course_id, {}).get("name", course_id)
                    anti_name = catalog_map.get(antireq, {}).get("name", antireq)
                    conflicts.append(
                        f"Anti-requisite conflict: Cannot enroll in '{target_name}' ({course_id}) because you have "
                        f"already completed mutually exclusive course '{anti_name}' ({antireq})."
                    )

    # -----------------------------------------------------------------------
    # CHECK 4: Credit Load Range Check [12, 24] Credits
    # -----------------------------------------------------------------------
    if total_credits < 12:
        conflicts.append(
            f"Credit Underload conflict: Proposed total credits ({total_credits} credits) is below the "
            f"minimum full-time threshold of 12 credits per semester."
        )
    elif total_credits > 24:
        conflicts.append(
            f"Credit Overload conflict: Proposed total credits ({total_credits} credits) exceeds the "
            f"maximum allowable cap of 24 credits per semester without Dean's formal waiver."
        )

    is_valid = (len(conflicts) == 0)

    return ConflictCheckResponse(
        is_valid=is_valid,
        total_credits=total_credits,
        conflicts=conflicts
    )


# ---------------------------------------------------------------------------
# 2. Course Catalog Listing Grouped by Semester
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 3. University Degree Requirements & Policy Listing
# ---------------------------------------------------------------------------
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
