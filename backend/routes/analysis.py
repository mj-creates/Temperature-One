"""
Graduation Risk & Academic Bottleneck Analysis Route
====================================================
Evaluates a student's graduation progress toward the 160-credit degree requirement:
- Credit deficit calculation (160 - earned credits)
- Academic standing classification (Good, Warning, Probation)
- Critical prerequisite gateway/bottleneck course identification
- Overall graduation risk level determination (LOW, MEDIUM, HIGH)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import sqlite3

from backend.database.database import get_db_connection
from backend.database.crud import get_student_by_regno
from backend.schemas import (
    BottleneckCourse,
    StudentRiskAnalysisResponse,
)

router = APIRouter(prefix="/api/students", tags=["Graduation Risk & Academic Analysis"])

TOTAL_GRADUATION_CREDITS_REQUIRED = 160

# Critical gateway courses that act as choke points for multiple upper-level electives
GATEWAY_BOTTLENECK_CATALOG: Dict[str, Dict[str, Any]] = {
    "Sub_1_1": {
        "name": "Introduction to Programming & Problem Solving",
        "reason": "Foundational programming gateway; prerequisite for 5 core second-year subjects."
    },
    "Sub_1_2": {
        "name": "Calculus & Analytical Geometry",
        "reason": "Foundational mathematics gateway; prerequisite for Linear Algebra and Probability & Statistics."
    },
    "Sub_1_7": {
        "name": "Digital Logic & Circuit Design",
        "reason": "Hardware foundation; prerequisite for Computer Architecture and Systems Design."
    },
    "Sub_2_1": {
        "name": "Data Structures and Algorithms",
        "reason": "Prerequisite for 4 upcoming core subjects including Algorithms, Distributed Systems, and ML."
    },
    "Sub_2_3": {
        "name": "Linear Algebra & Vector Spaces",
        "reason": "Key gateway for AI, Machine Learning, and Quantum Computing tracks; delays graduation if missed."
    },
    "Sub_2_4": {
        "name": "Computer Architecture & Microprocessors",
        "reason": "Prerequisite for Operating Systems and Cloud Infrastructure courses."
    },
    "Sub_2_9": {
        "name": "Relational Databases & SQL",
        "reason": "Gateway for Database Management Systems, Data Warehousing, and Big Data courses."
    },
    "Sub_3_3": {
        "name": "Design & Analysis of Algorithms",
        "reason": "Prerequisite for Machine Learning Systems and Senior Capstone Project."
    },
    "Sub_3_5": {
        "name": "Artificial Intelligence Concepts",
        "reason": "Gateway for Deep Learning, Reinforcement Learning, and Computer Vision specializations."
    },
}


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@router.get(
    "/{reg_no}/risk-analysis",
    response_model=StudentRiskAnalysisResponse,
    summary="Get Graduation Risk & Bottleneck Analysis",
    description="Evaluates student progression toward 160 graduation credits, identifying credit deficits, CGPA standing, and gateway course bottlenecks."
)
def get_graduation_risk_analysis(
    reg_no: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Performs deterministic academic audit for student:
    1. Computes earned credits and deficit toward 160-credit threshold.
    2. Classifies academic standing based on CGPA.
    3. Identifies critical gateway bottleneck courses for upcoming terms.
    4. Computes overall graduation risk score (LOW, MEDIUM, HIGH).
    """
    cursor = db.cursor()

    # Step 1: Query student profile
    cursor.execute(
        "SELECT RegNo, StudentName, Semester, CGPA, Goal FROM Students WHERE RegNo = ? COLLATE NOCASE;",
        (reg_no.strip(),)
    )
    student_row = cursor.fetchone()
    if not student_row:
        raise HTTPException(
            status_code=404,
            detail=f"Student with Registration Number '{reg_no}' not found in database."
        )

    current_semester = int(student_row["Semester"])
    cgpa = round(float(student_row["CGPA"]), 2)

    # Step 2: Query enrolled / completed subjects and sum earned credits
    cursor.execute(
        """
        SELECT ss.SubjectID, s.SubjectName, s.Credits, s.Semester
        FROM Student_Subjects ss
        JOIN Subjects s ON ss.SubjectID = s.SubjectID
        WHERE ss.RegNo = ? COLLATE NOCASE;
        """,
        (reg_no.strip(),)
    )
    enrolled_rows = cursor.fetchall()
    completed_subject_ids = {r["SubjectID"] for r in enrolled_rows if r["SubjectID"]}

    # Approximate cumulative credits earned:
    # If student is in Semester K, completed terms have ~20 credits each + current registered credits
    current_term_credits = sum(int(r["Credits"]) for r in enrolled_rows) or 20
    past_terms = max(0, current_semester - 1)
    total_credits_earned = (past_terms * 20) + current_term_credits

    credits_deficit = max(0, TOTAL_GRADUATION_CREDITS_REQUIRED - total_credits_earned)

    # Step 3: Academic Standing Classification
    if cgpa >= 6.5:
        academic_standing = "Good"
    elif cgpa >= 5.0:
        academic_standing = "Warning"
    else:
        academic_standing = "Probation"

    # Step 4: Identify Bottleneck Courses relevant for the student's progress
    bottlenecks: List[BottleneckCourse] = []

    for course_id, info in GATEWAY_BOTTLENECK_CATALOG.items():
        # Check if student has not completed this critical gateway yet
        if course_id not in completed_subject_ids:
            # Check if this course belongs to upcoming or current semester range
            parts = course_id.split("_")
            course_sem = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
            
            if course_sem >= current_semester or course_sem == current_semester + 1:
                bottlenecks.append(
                    BottleneckCourse(
                        course_id=course_id,
                        reason=info["reason"]
                    )
                )

    # Ensure at least the primary gateway for their career track is highlighted if bottlenecks list is empty
    if not bottlenecks:
        if current_semester <= 2:
            bottlenecks.append(
                BottleneckCourse(
                    course_id="Sub_2_1",
                    reason="Prerequisite for 4 upcoming core subjects including Algorithms and Distributed Systems"
                )
            )
            bottlenecks.append(
                BottleneckCourse(
                    course_id="Sub_2_3",
                    reason="Only offered in Spring, delays graduation if missed"
                )
            )
        else:
            bottlenecks.append(
                BottleneckCourse(
                    course_id="Sub_3_3",
                    reason="Prerequisite for 4 upcoming core subjects including Capstone & Machine Learning"
                )
            )

    # Step 5: Overall Graduation Risk Level Determination
    remaining_semesters = max(1, 8 - current_semester)
    required_pace = credits_deficit / remaining_semesters

    if academic_standing == "Probation" or required_pace > 24.0 or (current_semester >= 4 and cgpa < 6.0):
        graduation_risk_level = "HIGH"
    elif academic_standing == "Warning" or required_pace > 21.0 or cgpa < 7.0:
        graduation_risk_level = "MEDIUM"
    else:
        graduation_risk_level = "LOW"

    return StudentRiskAnalysisResponse(
        reg_no=student_row["RegNo"],
        total_credits_earned=total_credits_earned,
        credits_deficit=credits_deficit,
        current_cgpa=cgpa,
        academic_standing=academic_standing,
        bottleneck_courses=bottlenecks[:3],  # Top 3 most critical bottlenecks
        graduation_risk_level=graduation_risk_level
    )
