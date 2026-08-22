"""
Database CRUD and Repository functions for Academic Advising API.
Provides safe, parameterized SQLite queries.
"""

import sqlite3
from typing import List, Optional, Dict, Any


def get_students(
    conn: sqlite3.Connection,
    semester: Optional[int] = None,
    goal: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetches student summary records with optional semester and career goal filtering.
    """
    query = "SELECT RegNo, StudentName, Branch, Semester, CGPA, Goal FROM Students WHERE 1=1"
    params: List[Any] = []

    if semester is not None:
        query += " AND Semester = ?"
        params.append(semester)

    if goal is not None and goal.strip():
        query += " AND LOWER(Goal) LIKE LOWER(?)"
        params.append(f"%{goal.strip()}%")

    query += " ORDER BY RegNo ASC"

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    return [
        {
            "reg_no": row["RegNo"],
            "student_name": row["StudentName"],
            "branch": row["Branch"],
            "semester": row["Semester"],
            "cgpa": float(row["CGPA"]),
            "goal": row["Goal"],
        }
        for row in rows
    ]


def get_student_by_regno(conn: sqlite3.Connection, reg_no: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full student profile along with enrolled subjects and total credits.
    """
    cursor = conn.cursor()

    # 1. Fetch Student metadata (case-insensitive lookup)
    cursor.execute(
        "SELECT RegNo, StudentName, Branch, Semester, CGPA, Goal FROM Students WHERE RegNo = ? COLLATE NOCASE;",
        (reg_no.strip(),)
    )
    student_row = cursor.fetchone()
    if not student_row:
        return None

    # 2. Fetch enrolled subjects joined with Subjects catalog
    cursor.execute("""
        SELECT 
            sub.SubjectID, 
            sub.SubjectName, 
            sub.Semester, 
            sub.Credits, 
            ss.EnrollmentDate
        FROM Student_Subjects ss
        JOIN Subjects sub ON ss.SubjectID = sub.SubjectID
        WHERE ss.RegNo = ? COLLATE NOCASE
        ORDER BY LENGTH(sub.SubjectID), sub.SubjectID;
    """, (reg_no.strip(),))
    subject_rows = cursor.fetchall()

    enrolled_subjects = [
        {
            "subject_id": s["SubjectID"],
            "subject_name": s["SubjectName"],
            "semester": s["Semester"],
            "credits": s["Credits"],
            "enrollment_date": s["EnrollmentDate"],
        }
        for s in subject_rows
    ]

    total_credits = sum(s["credits"] for s in enrolled_subjects)

    return {
        "reg_no": student_row["RegNo"],
        "student_name": student_row["StudentName"],
        "branch": student_row["Branch"],
        "semester": student_row["Semester"],
        "cgpa": float(student_row["CGPA"]),
        "goal": student_row["Goal"],
        "total_registered_credits": total_credits,
        "enrolled_subjects": enrolled_subjects,
    }


def create_student(
    conn: sqlite3.Connection,
    reg_no: str,
    student_name: str,
    branch: str,
    semester: int,
    cgpa: float,
    goal: str,
    enrolled_subject_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Inserts a new student record and default subject enrollments into the database.
    """
    cursor = conn.cursor()
    clean_reg = reg_no.strip().upper()
    
    cursor.execute("""
        INSERT INTO Students (RegNo, StudentName, Branch, Semester, CGPA, Goal)
        VALUES (?, ?);
    """, (clean_reg, student_name.strip(), branch.strip(), semester, cgpa, goal.strip()))

    if not enrolled_subject_ids:
        cursor.execute("SELECT SubjectID FROM Subjects WHERE Semester = ? AND Branch = ? LIMIT 6;", (semester, branch.strip()))
        rows = cursor.fetchall()
        enrolled_subject_ids = [r[0] for r in rows]

    for sid in enrolled_subject_ids:
        cursor.execute("""
            INSERT OR IGNORE INTO Student_Subjects (RegNo, SubjectID)
            VALUES (?, ?);
        """, (clean_reg, sid))

    conn.commit()
    return get_student_by_regno(conn, clean_reg)


def get_all_subjects(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """
    Fetches all catalog subjects across all semesters.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SubjectID, SubjectName, Semester, Credits 
        FROM Subjects 
        ORDER BY Semester ASC, LENGTH(SubjectID) ASC, SubjectID ASC;
    """)
    rows = cursor.fetchall()

    return [
        {
            "subject_id": r["SubjectID"],
            "subject_name": r["SubjectName"],
            "semester": r["Semester"],
            "credits": r["Credits"],
            "enrollment_date": None,
        }
        for r in rows
    ]


def get_degree_requirements(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Fetches degree requirements from the Degree_Requirements table and parses them into structured policy fields.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT RuleKey, RuleValue, Description FROM Degree_Requirements ORDER BY RuleKey ASC;")
    rows = cursor.fetchall()

    rules_list = [
        {
            "rule_key": r["RuleKey"],
            "rule_value": r["RuleValue"],
            "description": r["Description"],
        }
        for r in rows
    ]

    rules_dict = {r["rule_key"]: r["rule_value"] for r in rules_list}

    total_credits = int(rules_dict.get("TOTAL_GRADUATION_CREDITS", 160))
    total_semesters = int(rules_dict.get("TOTAL_SEMESTERS", 8))
    subjects_per_sem = int(rules_dict.get("SUBJECTS_PER_SEMESTER", 6))
    semester_target = int(rules_dict.get("SEMESTER_CREDIT_TARGET", 20))
    min_cgpa = float(rules_dict.get("MIN_PASS_CGPA", 5.0))

    return {
        "total_graduation_credits": total_credits,
        "total_semesters": total_semesters,
        "subjects_per_semester": subjects_per_sem,
        "semester_credit_target": semester_target,
        "min_pass_cgpa": min_cgpa,
        "rules": rules_list,
    }
