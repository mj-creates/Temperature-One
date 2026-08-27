from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/counseling", tags=["Counseling Scheduling"])

class SessionBooking(BaseModel):
    student_id: str
    topic: str
    preferred_date: str

mock_db_sessions = []

@router.post("/book")
def book_session(req: SessionBooking):
    new_session = {
        "id": f"SESS_{len(mock_db_sessions)+100}",
        "student_id": req.student_id,
        "topic": req.topic,
        "date": req.preferred_date,
        "status": "CONFIRMED"
    }
    mock_db_sessions.append(new_session)
    return {"status": "success", "session": new_session}

@router.get("/student/{student_id}")
def get_student_sessions(student_id: str):
    user_sessions = [s for s in mock_db_sessions if s["student_id"] == student_id]
    return {"status": "success", "sessions": user_sessions}

