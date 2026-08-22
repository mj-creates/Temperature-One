from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import sqlite3
from pathlib import Path

# Connect directly to DB for this micro-route
DB_PATH = Path(__file__).resolve().parent.parent / "university.db"

router = APIRouter()

class SubstitutionResponse(BaseModel):
    original_subject: str
    original_name: str
    credits: int
    semester: int
    substitutes_found: int
    alternatives: List[Dict[str, Any]]

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@router.get("/{subject_id}/substitutes", response_model=SubstitutionResponse)
def get_subject_substitutes(subject_id: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Alternative Course Engine:
    Finds drop-in equivalent courses for a given SubjectID.
    Matches must share the same Semester level and provide at least the same Credits,
    ensuring graph-pathway constraints and credit limits are not broken.
    """
    cursor = conn.cursor()
    
    # 1. Fetch the original course details
    cursor.execute("""
        SELECT SubjectID, SubjectName, Semester, Credits 
        FROM Subjects 
        WHERE SubjectID = ? COLLATE NOCASE
    """, (subject_id,))
    
    original = cursor.fetchone()
    if not original:
        raise HTTPException(status_code=404, detail="Subject not found in catalog.")
        
    orig_id = original["SubjectID"]
    orig_name = original["SubjectName"]
    orig_sem = original["Semester"]
    orig_credits = original["Credits"]
    
    # 2. Query for drop-in substitutes
    # Criteria: Same semester (to respect prerequisites graph), same or more credits, excluding original.
    cursor.execute("""
        SELECT SubjectID, SubjectName, Credits
        FROM Subjects
        WHERE Semester = ? 
          AND Credits >= ?
          AND SubjectID != ?
        ORDER BY Credits ASC, SubjectName ASC
        LIMIT 5
    """, (orig_sem, orig_credits, orig_id))
    
    substitutes = cursor.fetchall()
    
    alts = []
    for sub in substitutes:
        alts.append({
            "subject_id": sub["SubjectID"],
            "subject_name": sub["SubjectName"],
            "credits": sub["Credits"],
            "substitution_match_score": "HIGH" if sub["Credits"] == orig_credits else "MEDIUM"
        })
        
    return SubstitutionResponse(
        original_subject=orig_id,
        original_name=orig_name,
        credits=orig_credits,
        semester=orig_sem,
        substitutes_found=len(alts),
        alternatives=alts
    )
