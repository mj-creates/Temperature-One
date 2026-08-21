"""
Schemas and data structures for Agent 4 - "The Background Check" (State Synthesizer).
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# Error Code Constants
STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
INVALID_DBMS_PAYLOAD = "INVALID_DBMS_PAYLOAD"


class AcademicState(BaseModel):
    """Academic standing and metrics parsed directly from DBMS records."""
    model_config = ConfigDict(extra="ignore")

    current_gpa: Optional[float] = Field(
        default=None,
        description="Current GPA/CGPA of the student, or null if unrecorded."
    )
    credits_earned: Optional[int] = Field(
        default=None,
        description="Total credits earned/enrolled, or null if unrecorded."
    )
    academic_standing: Optional[str] = Field(
        default=None,
        description="Academic standing classification (e.g., GOOD_STANDING, AT_RISK, HONORS) or null."
    )


class EngagementState(BaseModel):
    """Operational engagement and behavioral metrics parsed directly from DBMS records."""
    model_config = ConfigDict(extra="ignore")

    attendance_percentage: Optional[float] = Field(
        default=None,
        description="Recorded attendance percentage, or null if unrecorded."
    )
    last_activity_date: Optional[str] = Field(
        default=None,
        description="Timestamp or date of last recorded activity/enrollment, or null if unrecorded."
    )
    behavioral_flags: List[str] = Field(
        default_factory=list,
        description="List of recorded behavioral flags/disciplinary notices, or empty list."
    )


class StudentState(BaseModel):
    """
    Validated, structured Student State output schema for downstream agents.
    Strictly follows Agent 4 specifications.
    """
    model_config = ConfigDict(extra="ignore")

    student_id: str = Field(
        ...,
        description="Unique identifier / RegNo of the student."
    )
    record_timestamp: str = Field(
        ...,
        description="ISO-8601 or DBMS timestamp of the record extraction/synthesis."
    )
    account_status: str = Field(
        default="ACTIVE",
        description="Current status of the student account (e.g., ACTIVE, INACTIVE, SUSPENDED, PROBATION)."
    )
    academic_state: AcademicState = Field(
        default_factory=AcademicState,
        description="Academic standing and credit state."
    )
    engagement_state: EngagementState = Field(
        default_factory=EngagementState,
        description="Engagement and attendance state."
    )
    synthesis_summary: str = Field(
        ...,
        description="A precise, 2-sentence analytical summary of the student's current state based solely on DBMS facts."
    )


class Agent4ErrorResponse(BaseModel):
    """Standardized error protocol response for Agent 4."""
    model_config = ConfigDict(extra="ignore")

    status: str = Field(default="ERROR")
    error_code: str = Field(..., description="Machine-readable error identifier.")
    state: Optional[Any] = Field(default=None, description="Always null on error as per protocol.")
