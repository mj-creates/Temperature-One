"""
Backend Database Models & Entity Representations
================================================
Normalized data models aligned with SQLite schema and Pydantic schemas.
All student models strictly omit deprecated `CreditsObtained` and `CreditsRequired`
fields in favor of dynamic enrollment-calculated credits and branch assignments.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class StudentModel:
    """Relational model for Students table."""
    reg_no: str
    student_name: str
    branch: str
    semester: int
    cgpa: float
    goal: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reg_no": self.reg_no,
            "student_name": self.student_name,
            "branch": self.branch,
            "semester": self.semester,
            "cgpa": self.cgpa,
            "goal": self.goal,
        }


@dataclass
class SubjectModel:
    """Relational model for Subjects catalog table."""
    subject_id: str
    subject_name: str
    branch: str
    semester: int
    credits: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "branch": self.branch,
            "semester": self.semester,
            "credits": self.credits,
        }


@dataclass
class DegreeRequirementModel:
    """Relational model for Degree_Requirements catalog rule table."""
    rule_key: str
    rule_value: str
    description: Optional[str] = None


@dataclass
class PrerequisiteModel:
    """Relational model for Prerequisites graph edge table."""
    subject_id: str
    prereq_subject_id: str
    prereq_type: str  # HARD_PREREQ, COREQ, ANTIREQ


@dataclass
class CourseEquivalenceModel:
    """Relational model for Course_Equivalences substitution table."""
    subject_id: str
    equivalent_subject_id: str
    equivalence_type: str


@dataclass
class AcademicPolicyModel:
    """Relational model for Academic_Policies Graph-RAG table."""
    policy_id: str
    section: str
    title: str
    content: str
    category: str
    citation_code: str


@dataclass
class FacultyPetitionModel:
    """Relational model for Faculty_Petitions exception and audit table."""
    petition_id: str
    reg_no: str
    subject_id: str
    petition_type: str
    reason: str
    status: str = "PENDING"
    faculty_remarks: Optional[str] = None
    audit_hash: str = ""


@dataclass
class WaiverRequestModel:
    """Relational model for Waiver_Requests table."""
    id: Optional[int]
    reg_no: str
    course_id: str
    reason: str
    waiver_type: str
    status: str = "PENDING"
    approver_id: Optional[str] = None
    comments: Optional[str] = None
    created_at: Optional[str] = None
