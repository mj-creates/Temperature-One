from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import sqlite3
import random
try:
    from backend.database.database import get_db_connection
except ImportError:
    from database.database import get_db_connection

router = APIRouter(prefix="/api/teacher", tags=["Teacher Dashboard"])

@router.get("/students")
def get_all_students_overview():
    """Returns an aggregated list of students and their risk profiles for the Teacher Dashboard."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Fetch basic student info with correct database column mappings
        cursor.execute("SELECT RegNo as student_id, StudentName as name, Branch as department, CGPA as current_gpa, Semester as semester, Goal as goal FROM Students")
        students = cursor.fetchall()

        
        result = []
        for s in students:
            # Calculate mock risk score based on GPA and semester (could be enhanced by Graph-RAG in real app)
            base_risk = 0
            if s['current_gpa'] < 6.0:
                base_risk += 50
            elif s['current_gpa'] < 7.5:
                base_risk += 20
                
            # Randomly mock missing prerequisites for demo purposes
            missing_prereqs = random.choice([True, False, False])
            if missing_prereqs:
                base_risk += 30
                
            risk_level = "HIGH" if base_risk > 60 else "MEDIUM" if base_risk > 30 else "LOW"
            
            result.append({
                "student_id": s['student_id'],
                "name": s['name'],
                "department": s['department'],
                "cgpa": s['current_gpa'],
                "semester": s['semester'],
                "risk_score": min(base_risk, 100),
                "risk_level": risk_level,
                "missing_prerequisites": missing_prereqs
            })
            
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
