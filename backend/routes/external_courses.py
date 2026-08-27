from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/api/external-courses", tags=["External Courses Auto-Enrollment"])

class EnrollmentRequest(BaseModel):
    student_id: str
    missing_skill: str

@router.post("/auto-enroll")
def auto_enroll_student(req: EnrollmentRequest):
    # Mocking Coursera / edX API Integration
    mock_courses = [
        f"Coursera: Fundamentals of {req.missing_skill.capitalize()}",
        f"edX: Introduction to {req.missing_skill.capitalize()} (HarvardX)",
        f"Udacity: {req.missing_skill.capitalize()} Nanodegree Prep"
    ]
    
    selected_course = random.choice(mock_courses)
    
    return {
        "status": "success",
        "message": f"Successfully enrolled student {req.student_id} into {selected_course}",
        "course_enrolled": selected_course,
        "platform": selected_course.split(":")[0],
        "cost": "Free (University Sponsored)"
    }

