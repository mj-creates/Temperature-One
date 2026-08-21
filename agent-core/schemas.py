"""
Schemas and data structures for Anti Gravity autonomous pipeline agents:
- Agent 4: "The Background Check" (State Synthesizer)
- Agent 2: "The Matrix" (Graph Navigator & Pathfinder)
"""

from typing import List, Optional, Any, Union, Dict
from pydantic import BaseModel, Field, ConfigDict


# ===========================================================================
# AGENT 4 CONSTANTS & MODELS
# ===========================================================================
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


# ===========================================================================
# AGENT 2 (THE MATRIX) CONSTANTS & MODELS
# ===========================================================================
STATUS_VALID = "VALID"
STATUS_UNREACHABLE = "UNREACHABLE"
STATUS_PATH_UNREACHABLE = "PATH_UNREACHABLE"
STATUS_GRAPH_ERROR = "GRAPH_ERROR"
STATUS_ALREADY_ACHIEVED = "ALREADY_ACHIEVED"

ERROR_MISSING_CRITICAL_NODE = "MISSING_CRITICAL_NODE"
ERROR_CYCLIC_DEPENDENCY = "CYCLIC_DEPENDENCY"


class PathStep(BaseModel):
    """A chronological sequence step/block in the generated path."""
    model_config = ConfigDict(extra="ignore")

    step_number: int = Field(..., description="Sequence step index (1-indexed).")
    step_label: str = Field(..., description="Descriptive label (e.g., Term 1, Semester 2, Sprint A).")
    nodes_to_complete: List[str] = Field(..., description="Array of exact node IDs to complete in this step.")
    step_total_credits_or_effort: float = Field(
        ..., description="Total credits or effort units allocated in this step."
    )


class MatrixPathResponse(BaseModel):
    """
    Validated, structured output schema for Agent - The Matrix.
    """
    model_config = ConfigDict(extra="ignore")

    student_id: str = Field(..., description="Target student identifier.")
    target_node: str = Field(..., description="Target node or degree milestone.")
    path_status: str = Field(
        default="VALID",
        description="Status of the computed path (e.g., VALID, UNREACHABLE, ALREADY_ACHIEVED)."
    )
    total_steps_required: int = Field(..., description="Total chronological steps needed to reach target.")
    path_sequence: List[PathStep] = Field(
        default_factory=list,
        description="Chronologically ordered sequence of steps to complete."
    )
    bottlenecks: List[str] = Field(
        default_factory=list,
        description="Array of node IDs that act as critical chokepoints/gateways."
    )
    matrix_analysis: str = Field(
        ...,
        description="A strict, 2-sentence logical proof explaining why this path is the most optimal route and confirming all prerequisites are satisfied."
    )


class MatrixErrorResponse(BaseModel):
    """Standardized error/impasse response for Agent - The Matrix."""
    model_config = ConfigDict(extra="ignore")

    status: str = Field(..., description="Status flag: PATH_UNREACHABLE, GRAPH_ERROR, ALREADY_ACHIEVED.")
    error: Optional[str] = Field(default=None, description="Specific error reason or null.")
    sequence: List[Any] = Field(default_factory=list, description="Empty sequence array.")
