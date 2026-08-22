"""
Schemas and data structures for the decentralized multi-agent academic advising platform:
- Agent 1: Nexus (Front Desk & Orchestrator)
- Agent 2: The Matrix (Graph Navigator & Pathfinder)
- Agent 3: Vector (Future Scope & Career Trajectory Engine)
- Agent 4: The Background Check (State Synthesizer)
- Agent 5: Codex (Graph-RAG Policy & Citation Engine)
- Agent 6: Sentinel (Formal Constraint & Faculty Verifier)
"""

from typing import List, Optional, Any, Union, Dict
from pydantic import BaseModel, Field, ConfigDict


# ===========================================================================
# AGENT 4 CONSTANTS & MODELS (THE BACKGROUND CHECK)
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
        description="Academic standing classification (e.g., HONORS, GOOD_STANDING, MONITORED, ACADEMIC_PROBATION)."
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
    """Validated, structured Student State output schema for downstream agents."""
    model_config = ConfigDict(extra="ignore")

    student_id: str = Field(..., description="Unique identifier / RegNo of the student.")
    student_name: Optional[str] = Field(default=None, description="Full legal name of the student.")
    semester: Optional[int] = Field(default=None, description="Current semester index (1-4).")
    career_goal: Optional[str] = Field(default=None, description="Target career track.")
    record_timestamp: str = Field(..., description="ISO-8601 or DBMS timestamp of extraction.")
    account_status: str = Field(default="ACTIVE", description="Current account status.")
    academic_state: AcademicState = Field(default_factory=AcademicState)
    engagement_state: EngagementState = Field(default_factory=EngagementState)
    enrolled_subjects: List[Dict[str, Any]] = Field(default_factory=list)
    synthesis_summary: str = Field(
        ...,
        description="A precise analytical summary of the student's current state based solely on DBMS facts."
    )


class Agent4ErrorResponse(BaseModel):
    """Standardized error protocol response for Agent 4."""
    model_config = ConfigDict(extra="ignore")

    status: str = Field(default="ERROR")
    error_code: str = Field(..., description="Machine-readable error identifier.")
    state: Optional[Any] = Field(default=None)


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
    """A chronological sequence step/block in the generated pathway."""
    model_config = ConfigDict(extra="ignore")

    step_number: int = Field(..., description="Sequence step index (1-indexed).")
    step_label: str = Field(..., description="Descriptive label (e.g., Semester 2, Term 3).")
    nodes_to_complete: List[str] = Field(..., description="Array of exact node IDs to complete in this step.")
    nodes_details: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Course metadata.")
    step_total_credits_or_effort: float = Field(..., description="Total credits allocated in this step.")


class MatrixPathResponse(BaseModel):
    """Validated output schema for Agent - The Matrix."""
    model_config = ConfigDict(extra="ignore")

    student_id: str = Field(..., description="Target student identifier.")
    target_node: str = Field(..., description="Target node or degree milestone.")
    path_status: str = Field(default="VALID", description="Status of computed path.")
    total_steps_required: int = Field(..., description="Total steps needed to reach target.")
    path_sequence: List[PathStep] = Field(default_factory=list)
    bottlenecks: List[str] = Field(default_factory=list)
    matrix_analysis: str = Field(
        ...,
        description="Logical proof explaining why this path is the most optimal route."
    )


class MatrixErrorResponse(BaseModel):
    """Standardized error/impasse response for Agent - The Matrix."""
    model_config = ConfigDict(extra="ignore")

    status: str = Field(..., description="Status flag.")
    error: Optional[str] = Field(default=None, description="Specific error reason.")
    sequence: List[Any] = Field(default_factory=list)


# ===========================================================================
# AGENT 3 (VECTOR) MODELS
# ===========================================================================
class MomentumPlan(BaseModel):
    """Strategic career momentum plan generated by Agent 3."""
    model_config = ConfigDict(extra="ignore")

    student_goal: str
    actionable_project: str
    internship_target: str
    next_level_milestone: str
    target_certifications: List[str] = Field(default_factory=list)
    raw_markdown: str


# ===========================================================================
# AGENT 5 (CODEX GRAPH-RAG) MODELS
# ===========================================================================
class PolicyCitation(BaseModel):
    """Citation metadata for grounded academic advising."""
    model_config = ConfigDict(extra="ignore")

    policy_id: str
    section: str
    title: str
    citation_code: str
    relevance_snippet: str
    category: str


class GraphRAGQueryResult(BaseModel):
    """Structured output from Codex Graph-RAG policy retrieval."""
    model_config = ConfigDict(extra="ignore")

    query: str
    matched_policies: List[PolicyCitation] = Field(default_factory=list)
    synthesis: str
    traceable_citations: List[str] = Field(default_factory=list)


# ===========================================================================
# CONFLICT RESOLUTION & DIAGNOSTICS MODELS
# ===========================================================================
class ConflictItem(BaseModel):
    """Represents an identified academic or prerequisite conflict."""
    model_config = ConfigDict(extra="ignore")

    conflict_id: str
    conflict_type: str = Field(..., description="PREREQUISITE_MISSING, CREDIT_OVERLOAD, COREQUISITE_VIOLATION, ANTIREQUISITE_COLLISION, GPA_PROBATION_RISK")
    severity: str = Field(..., description="CRITICAL, WARNING, INFO")
    affected_courses: List[str] = Field(default_factory=list)
    description: str
    remedy_recommendation: str
    policy_citation: Optional[str] = None


class ConflictDiagnosticReport(BaseModel):
    """Comprehensive conflict assessment report for a student."""
    model_config = ConfigDict(extra="ignore")

    student_id: str
    has_conflicts: bool
    critical_count: int
    warning_count: int
    conflicts: List[ConflictItem] = Field(default_factory=list)
    graduation_risk_score: float = Field(default=0.0, description="0.0 (Safe) to 1.0 (High Risk)")
    summary: str


# ===========================================================================
# AGENT 6 (SENTINEL & FACULTY PORTAL) MODELS
# ===========================================================================
class FacultyPetitionCreate(BaseModel):
    """Payload to create a new formal waiver or overload petition."""
    model_config = ConfigDict(extra="ignore")

    reg_no: str
    subject_id: str
    petition_type: str = Field(..., description="PREREQUISITE_WAIVER, CREDIT_OVERLOAD, COURSE_SUBSTITUTION, SPECIAL_PERMISSION")
    reason: str


class FacultyPetitionRecord(BaseModel):
    """A formal faculty petition record with audit trail."""
    model_config = ConfigDict(extra="ignore")

    petition_id: str
    reg_no: str
    student_name: Optional[str] = None
    subject_id: str
    subject_name: Optional[str] = None
    petition_type: str
    reason: str
    status: str = Field(default="PENDING", description="PENDING, APPROVED, REJECTED")
    faculty_remarks: Optional[str] = None
    timestamp: str
    audit_hash: str


class FacultyActionPayload(BaseModel):
    """Payload for faculty approval or rejection."""
    model_config = ConfigDict(extra="ignore")

    action: str = Field(..., description="APPROVE or REJECT")
    faculty_remarks: str


# ===========================================================================
# MULTI-AGENT ADVISING PIPELINE FULL PAYLOAD
# ===========================================================================
class AdvisingSessionResponse(BaseModel):
    """Complete multi-agent pipeline unified response."""
    model_config = ConfigDict(extra="ignore")

    session_id: str
    student_id: str
    student_name: str
    current_semester: int
    cgpa: float
    career_goal: str
    academic_standing: str

    student_state: StudentState
    degree_pathway: MatrixPathResponse
    conflict_report: ConflictDiagnosticReport
    career_vector: MomentumPlan
    graph_rag_advising: GraphRAGQueryResult
    faculty_petitions: List[FacultyPetitionRecord] = Field(default_factory=list)

    advising_narrative: str
    citations: List[str] = Field(default_factory=list)
    agent_telemetry: List[Dict[str, Any]] = Field(default_factory=list)
