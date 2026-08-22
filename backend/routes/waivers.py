"""
Faculty Waiver & Exception Approval Workflow Route
===================================================
Provides REST APIs for:
- Student Waiver Submission (/api/waivers/request)
- Faculty/Dean Approval or Rejection (/api/waivers/{id}/approve)
- Listing & Filtering Waiver Requests (/api/waivers)
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
import sqlite3

from backend.database.database import get_db_connection
from backend.domain_schemas import (
    WaiverCreateRequest,
    WaiverApprovalRequest,
    WaiverResponse,
)

router = APIRouter(prefix="/api/waivers", tags=["Faculty Waivers & Approvals"])


def get_db():
    """Dependency to provide SQLite database connection with auto-table migration and close."""
    conn = get_db_connection()
    ensure_waiver_table(conn)
    try:
        yield conn
    finally:
        conn.close()


def ensure_waiver_table(conn: sqlite3.Connection):
    """Auto-creates the Waiver_Requests table if it does not exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Waiver_Requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT NOT NULL,
            course_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            waiver_type TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            approver_id TEXT,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# 1. Submit New Waiver Request
# ---------------------------------------------------------------------------
@router.post(
    "/request",
    response_model=WaiverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new academic waiver request",
    description="Allows a student to submit a prerequisite override or credit overload request."
)
def create_waiver_request(
    request: WaiverCreateRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Submits a new waiver request into the Waiver_Requests table with initial status 'PENDING'.
    """
    cursor = db.cursor()

    # Verify student exists
    cursor.execute(
        "SELECT RegNo FROM Students WHERE RegNo = ? COLLATE NOCASE;",
        (request.reg_no.strip(),)
    )
    if not cursor.fetchone():
        raise HTTPException(
            status_code=404,
            detail=f"Student with Registration Number '{request.reg_no}' not found in database."
        )

    # Insert waiver record
    cursor.execute(
        """
        INSERT INTO Waiver_Requests (reg_no, course_id, reason, waiver_type, status)
        VALUES (?, ?, ?, ?, 'PENDING');
        """,
        (
            request.reg_no.strip(),
            request.course_id.strip(),
            request.reason.strip(),
            request.waiver_type.strip(),
        )
    )
    db.commit()
    new_id = cursor.lastrowid

    # Fetch newly created record
    cursor.execute("SELECT * FROM Waiver_Requests WHERE id = ?;", (new_id,))
    row = cursor.fetchone()

    return WaiverResponse(
        id=int(row["id"]),
        reg_no=row["reg_no"],
        course_id=row["course_id"],
        reason=row["reason"],
        waiver_type=row["waiver_type"],
        status=row["status"],
        approver_id=row["approver_id"],
        comments=row["comments"],
        created_at=str(row["created_at"])
    )


# ---------------------------------------------------------------------------
# 2. Faculty / Dean Waiver Approval or Rejection
# ---------------------------------------------------------------------------
@router.post(
    "/{id}/approve",
    response_model=WaiverResponse,
    summary="Approve or reject a waiver request",
    description="Faculty/Dean endpoint to update waiver status to 'APPROVED' or 'REJECTED' with comments."
)
def process_waiver_approval(
    id: int,
    request: WaiverApprovalRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Updates the status and approver audit notes for a specified waiver request ID.
    """
    status_upper = request.status.strip().upper()
    if status_upper not in ("APPROVED", "REJECTED"):
        raise HTTPException(
            status_code=400,
            detail="Status must be either 'APPROVED' or 'REJECTED'."
        )

    cursor = db.cursor()

    # Check if waiver exists
    cursor.execute("SELECT * FROM Waiver_Requests WHERE id = ?;", (id,))
    existing = cursor.fetchone()
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Waiver request with ID {id} not found."
        )

    # Update record
    cursor.execute(
        """
        UPDATE Waiver_Requests
        SET status = ?, approver_id = ?, comments = ?
        WHERE id = ?;
        """,
        (
            status_upper,
            request.approver_id.strip(),
            request.comments.strip() if request.comments else None,
            id
        )
    )
    db.commit()

    # Fetch updated record
    cursor.execute("SELECT * FROM Waiver_Requests WHERE id = ?;", (id,))
    row = cursor.fetchone()

    return WaiverResponse(
        id=int(row["id"]),
        reg_no=row["reg_no"],
        course_id=row["course_id"],
        reason=row["reason"],
        waiver_type=row["waiver_type"],
        status=row["status"],
        approver_id=row["approver_id"],
        comments=row["comments"],
        created_at=str(row["created_at"])
    )


# ---------------------------------------------------------------------------
# 3. List & Filter Waiver Requests
# ---------------------------------------------------------------------------
@router.get(
    "",
    response_model=List[WaiverResponse],
    summary="List all waiver requests",
    description="Returns all waiver records with optional filtering by status (PENDING, APPROVED, REJECTED) or student reg_no."
)
def list_waivers(
    status: Optional[str] = Query(None, description="Filter by status (e.g. PENDING, APPROVED, REJECTED)"),
    reg_no: Optional[str] = Query(None, description="Filter by student registration number (e.g. REG1001)"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves a list of academic waiver requests matching query parameters.
    """
    cursor = db.cursor()
    query = "SELECT * FROM Waiver_Requests WHERE 1=1"
    params = []

    if status:
        query += " AND UPPER(status) = ?"
        params.append(status.strip().upper())
    if reg_no:
        query += " AND UPPER(reg_no) = ?"
        params.append(reg_no.strip().upper())

    query += " ORDER BY id DESC;"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    return [
        WaiverResponse(
            id=int(r["id"]),
            reg_no=r["reg_no"],
            course_id=r["course_id"],
            reason=r["reason"],
            waiver_type=r["waiver_type"],
            status=r["status"],
            approver_id=r["approver_id"],
            comments=r["comments"],
            created_at=str(r["created_at"])
        )
        for r in rows
    ]
