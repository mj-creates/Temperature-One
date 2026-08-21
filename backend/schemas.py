"""
Pydantic Request & Response Schemas for the Academic Advising API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Student Schemas
# ---------------------------------------------------------------------------

class StudentSummary(BaseModel):
    """Summary representation of a student record."""
    model_config = ConfigDict(from_attributes=True)

    reg_no: str = Field(..., description="Unique student registration number, e.g., REG1001", examples=["REG1001"])
    student_name: str = Field(..., description="Full name of the student", examples=["Aarav Sharma"])
    semester: int = Field(..., ge=1, le=8, description="Current semester of study (1 to 4)", examples=[2])
    cgpa: float = Field(..., ge=0.0, le=10.0, description="Cumulative Grade Point Average", examples=[8.45])
    goal: str = Field(..., description="Target career track or academic specialization", examples=["Data Scientist"])


class SubjectItem(BaseModel):
    """Representation of an individual subject in curriculum or enrollment."""
    model_config = ConfigDict(from_attributes=True)

    subject_id: str = Field(..., description="Course code / identifier", examples=["Sub_1_1"])
    subject_name: str = Field(..., description="Title of the course", examples=["Introduction to Programming"])
    semester: int = Field(..., ge=1, le=8, description="Semester level of the course", examples=[1])
    credits: int = Field(..., ge=1, le=10, description="Credit units assigned to this subject", examples=[4])
    enrollment_date: Optional[str] = Field(None, description="Timestamp of enrollment if applicable")


class StudentDetail(BaseModel):
    """Detailed student profile including current subject enrollments and total credits."""
    model_config = ConfigDict(from_attributes=True)

    reg_no: str = Field(..., description="Unique student registration number", examples=["REG1001"])
    student_name: str = Field(..., description="Full name of the student", examples=["Aarav Sharma"])
    semester: int = Field(..., description="Current enrolled semester", examples=[2])
    cgpa: float = Field(..., description="Current CGPA", examples=[8.45])
    goal: str = Field(..., description="Declared career goal", examples=["AI Researcher"])
    total_registered_credits: int = Field(..., description="Sum of credits for enrolled subjects", examples=[20])
    enrolled_subjects: List[SubjectItem] = Field(default_factory=list, description="List of currently enrolled subjects")


# ---------------------------------------------------------------------------
# Subject Catalog & Degree Requirements Schemas
# ---------------------------------------------------------------------------

class SubjectsBySemesterResponse(BaseModel):
    """Catalog of curriculum subjects grouped by semester level."""
    total_subjects: int = Field(..., description="Total count of subjects in catalog", examples=[60])
    semesters: Dict[str, List[SubjectItem]] = Field(..., description="Subjects grouped by semester label")
    all_subjects: List[SubjectItem] = Field(..., description="Flat list of all subjects")


class DegreeRuleItem(BaseModel):
    """Individual degree rule or policy constraint."""
    rule_key: str = Field(..., description="Identifier key of the rule", examples=["TOTAL_GRADUATION_CREDITS"])
    rule_value: str = Field(..., description="Configured value for the rule", examples=["160"])
    description: Optional[str] = Field(None, description="Human-readable explanation of the requirement")


class DegreeRequirementsResponse(BaseModel):
    """Complete degree policy and graduation requirement metadata."""
    total_graduation_credits: int = Field(default=160, description="Minimum credits required to graduate")
    total_semesters: int = Field(default=8, description="Standard undergraduate degree duration")
    subjects_per_semester: int = Field(default=6, description="Mandatory enrolled subjects per semester")
    semester_credit_target: int = Field(default=20, description="Target average credits per semester")
    min_pass_cgpa: float = Field(default=5.0, description="Minimum CGPA required for good standing")
    rules: List[DegreeRuleItem] = Field(default_factory=list, description="Full raw list of degree requirements from database")


# ---------------------------------------------------------------------------
# Agent Orchestration Schemas
# ---------------------------------------------------------------------------

class AgentBackgroundCheckResponse(BaseModel):
    """Response returned by Agent 4 (The Background Check)."""
    reg_no: str = Field(..., description="Student registration number verified", examples=["REG1001"])
    verified: bool = Field(default=True, description="Indicates whether student record was verified in DBMS")
    total_credits_earned: int = Field(..., description="Total credits earned or currently enrolled", examples=[19])
    backlogs: List[str] = Field(default_factory=list, description="List of recorded backlogs or unfulfilled prerequisites")
    prerequisites_satisfied: bool = Field(default=True, description="True if no prerequisite conflicts or hold flags exist")
    student_state: Optional[Dict[str, Any]] = Field(None, description="Full validated StudentState JSON structure")
    synthesis_summary: Optional[str] = Field(None, description="2-sentence analytical summary synthesized by Agent 4")


class AdvisingSessionRequest(BaseModel):
    """Input payload to start or continue an advising session with Nexus (Agent 1)."""
    reg_no: str = Field(..., description="Student registration number", examples=["REG1001"])
    message: Optional[str] = Field(None, description="Optional custom user question, prompt, or goal override", examples=["I want to specialize in AI"])
    session_id: Optional[str] = Field(None, description="Optional existing session ID for multi-turn conversations", examples=["sess_1001_abc"])


class AdvisingSessionResponse(BaseModel):
    """Response returned after processing an advising session through Nexus (Agent 1)."""
    session_id: str = Field(..., description="Unique session identifier for the advising conversation")
    reg_no: str = Field(..., description="Student registration number")
    student_name: str = Field(..., description="Student full name")
    current_semester: int = Field(..., description="Current semester of the student")
    goal: str = Field(..., description="Current career goal")
    advisor_greeting: str = Field(..., description="Front desk welcoming message from Nexus (Agent 1)")
    advisor_response: str = Field(..., description="Response generated from agent orchestration")
    background_check: Optional[Dict[str, Any]] = None
    momentum_plan: Optional[str] = None


# ---------------------------------------------------------------------------
# Matrix (Agent 2) Pathfinding Schemas
# ---------------------------------------------------------------------------

class MatrixPathRequest(BaseModel):
    """Input payload to compute a prerequisite path using Agent 2 (The Matrix)."""
    student_id: str = Field(..., description="Student registration number", examples=["REG1001"])
    target_node: str = Field(..., description="Target course ID to achieve", examples=["Sub_4_1"])
    completed_nodes: Optional[List[str]] = Field(None, description="Optional override list of completed course IDs")
    max_credits_per_step: float = Field(default=20.0, description="Max credits allowed per semester step")


class PathStep(BaseModel):
    """A chronological sequence step in the generated prerequisite path."""
    step_number: int = Field(..., description="Sequence step index (1-indexed)")
    step_label: str = Field(..., description="Semester or term label")
    nodes_to_complete: List[str] = Field(..., description="Course IDs to take in this step")
    step_total_credits_or_effort: float = Field(..., description="Sum of credits allocated in this step")


class MatrixPathResponse(BaseModel):
    """Response returned by Agent 2 (The Matrix) containing topologically sorted schedule."""
    student_id: str = Field(..., description="Student registration number")
    target_node: str = Field(..., description="Target course ID")
    path_status: str = Field(default="VALID", description="Status: VALID, PATH_UNREACHABLE, ALREADY_ACHIEVED, GRAPH_ERROR")
    total_steps_required: int = Field(default=0, description="Total chronological semester stages required")
    path_sequence: List[PathStep] = Field(default_factory=list, description="Chronologically ordered sequence of course stages")
    bottlenecks: List[str] = Field(default_factory=list, description="Critical bottleneck/gateway course IDs")
    matrix_analysis: str = Field(..., description="2-sentence analytical proof of path optimality and prerequisite satisfaction")
    raw_matrix_output: Optional[Dict[str, Any]] = None
