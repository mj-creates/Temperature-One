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
    momentum_plan: Optional[Any] = None



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


# ---------------------------------------------------------------------------
# Codex (Agent 5) Graph-RAG Policy Query Schemas
# ---------------------------------------------------------------------------

class PolicyQueryRequest(BaseModel):
    """Input payload to query the Graph-RAG policy engine (Agent 5 - Codex)."""
    query: str = Field(
        ...,
        description="Natural language question or policy query",
        examples=["What are the prerequisites and credit rules for Operating Systems?"]
    )


class PolicyQueryResponse(BaseModel):
    """Response model representing verified policy constraints with graph citation."""
    query: str = Field(..., description="Original input query")
    target_subject: str = Field(..., description="Target subject or academic policy identified", examples=["Operating Systems Architecture"])
    required_prerequisites: List[str] = Field(
        default_factory=list,
        description="Array of required prerequisite course names/IDs",
        examples=[["Computer Architecture & Microprocessors", "Data Structures and Algorithms"]]
    )
    credit_value: int = Field(..., description="Course credit value or credit limit", examples=[4])
    special_rules: str = Field(default="NONE", description="Special constraints or conditions", examples=["NONE"])
    graph_citation: str = Field(..., description="Exact traceable graph citation", examples=["[Source: CS_Curriculum_Section_3.2_Node_OS]"])


# ---------------------------------------------------------------------------
# Curriculum Prerequisite & Credit Conflict Check Schemas
# ---------------------------------------------------------------------------

class ConflictCheckRequest(BaseModel):
    """Input payload to check prerequisite, co-requisite, anti-requisite, and credit conflicts."""
    reg_no: str = Field(
        ...,
        description="Student registration identifier (e.g. REG1001)",
        examples=["REG1001"]
    )
    proposed_courses: List[str] = Field(
        ...,
        description="List of exactly 6 proposed subject IDs to enroll in for upcoming term",
        examples=[["Sub_2_1", "Sub_2_2", "Sub_2_3", "Sub_2_4", "Sub_2_5", "Sub_2_6"]]
    )


class ConflictCheckResponse(BaseModel):
    """Result of the 4-step formal conflict verification check."""
    is_valid: bool = Field(..., description="True if no prerequisite, co-requisite, anti-requisite, or credit conflicts exist")
    total_credits: int = Field(..., description="Sum of credits for the proposed course schedule", examples=[20])
    conflicts: List[str] = Field(
        default_factory=list,
        description="List of human-readable conflict violation messages. Empty if is_valid is True."
    )


# ---------------------------------------------------------------------------
# Curriculum Knowledge Graph Schemas (React Flow & D3.js Compatible)
# ---------------------------------------------------------------------------

class GraphNode(BaseModel):
    """Represents a node (course) in the Curriculum Knowledge Graph."""
    id: str = Field(..., description="Unique Subject ID (e.g. Sub_1_1)", examples=["Sub_1_1"])
    label: str = Field(..., description="Human-readable subject name", examples=["Introduction to Programming"])
    semester: int = Field(..., description="Semester level (1 to 4)", examples=[1])
    credits: int = Field(..., description="Course credit value (3 or 4)", examples=[4])


class GraphEdge(BaseModel):
    """Represents a directed edge (dependency) between curriculum nodes."""
    id: str = Field(..., description="Unique Edge ID (e.g. e_Sub_1_1-Sub_2_1)", examples=["e_Sub_1_1-Sub_2_1"])
    source: str = Field(..., description="Source Subject ID", examples=["Sub_1_1"])
    target: str = Field(..., description="Target Subject ID", examples=["Sub_2_1"])
    type: str = Field(..., description="Dependency type: prerequisite, corequisite, or antirequisite", examples=["prerequisite"])
    label: str = Field(..., description="Visual relationship label", examples=["Requires"])


class CurriculumGraphResponse(BaseModel):
    """Complete Knowledge Graph payload ready for React Flow, Cytoscape, or D3.js."""
    nodes: List[GraphNode] = Field(..., description="Array of all curriculum nodes")
    edges: List[GraphEdge] = Field(..., description="Array of directed dependency edges")


# ---------------------------------------------------------------------------
# Graduation Risk & Bottleneck Analysis Schemas
# ---------------------------------------------------------------------------

class BottleneckCourse(BaseModel):
    """Represents a bottleneck or gateway course impacting academic progression."""
    course_id: str = Field(..., description="Course Subject ID", examples=["Sub_2_1"])
    reason: str = Field(..., description="Explanation of why this course is a critical gateway", examples=["Prerequisite for 4 upcoming core subjects"])


class StudentRiskAnalysisResponse(BaseModel):
    """Structured graduation risk assessment and bottleneck evaluation."""
    reg_no: str = Field(..., description="Student registration identifier", examples=["REG1001"])
    total_credits_earned: int = Field(..., description="Total cumulative credits earned", examples=[45])
    credits_deficit: int = Field(..., description="Deficit towards 160 graduation credits requirement", examples=[115])
    current_cgpa: float = Field(..., description="Current cumulative grade point average", examples=[6.8])
    academic_standing: str = Field(..., description="Academic standing: Good, Warning, or Probation", examples=["Good"])
    bottleneck_courses: List[BottleneckCourse] = Field(
        default_factory=list,
        description="Identified gateway/bottleneck courses"
    )
    graduation_risk_level: str = Field(..., description="Overall risk classification: LOW, MEDIUM, or HIGH", examples=["MEDIUM"])


# ---------------------------------------------------------------------------
# Faculty Waiver / Exception Workflow Schemas
# ---------------------------------------------------------------------------

class WaiverCreateRequest(BaseModel):
    """Input payload to submit a new academic waiver request."""
    reg_no: str = Field(..., description="Student registration identifier", examples=["REG1001"])
    course_id: str = Field(..., description="Target course ID for waiver", examples=["Sub_3_1"])
    reason: str = Field(..., description="Justification or evidence for waiver", examples=["Completed equivalent MOOC course on Coursera with verified certificate."])
    waiver_type: str = Field(default="PREREQUISITE_OVERRIDE", description="Type of waiver: PREREQUISITE_OVERRIDE or CREDIT_OVERLOAD", examples=["PREREQUISITE_OVERRIDE"])


class WaiverApprovalRequest(BaseModel):
    """Input payload for faculty/Dean to approve or reject a waiver."""
    approver_id: str = Field(..., description="Faculty or Dean identifier", examples=["FAC_DEAN_CS01"])
    status: str = Field(..., description="Approval status: APPROVED or REJECTED", examples=["APPROVED"])
    comments: Optional[str] = Field(None, description="Faculty review comments or conditions", examples=["Syllabus alignment verified. Waiver granted."])


class WaiverResponse(BaseModel):
    """Structured representation of an academic waiver request record."""
    id: int = Field(..., description="Unique auto-incremented waiver request ID")
    reg_no: str = Field(..., description="Student registration identifier")
    course_id: str = Field(..., description="Target course ID")
    reason: str = Field(..., description="Student's justification")
    waiver_type: str = Field(..., description="Waiver category")
    status: str = Field(..., description="Current status: PENDING, APPROVED, REJECTED")
    approver_id: Optional[str] = Field(None, description="Approving faculty ID")
    comments: Optional[str] = Field(None, description="Faculty review remarks")
    created_at: str = Field(..., description="Timestamp of submission")


# ---------------------------------------------------------------------------
# Unified Multi-Agent Orchestrator Schemas
# ---------------------------------------------------------------------------

class OrchestratorRequest(BaseModel):
    """Input payload to trigger the unified 5-agent advising pipeline."""
    student_id: str = Field(..., description="Student registration identifier (e.g. REG1001)", examples=["REG1001"])
    user_query: str = Field(..., description="Target career goal or academic advising query", examples=["I want to specialize in AI and Cloud Architecture"])


class OrchestratorResponse(BaseModel):
    """Aggregated advising output produced across the 5-agent pipeline with circuit breaker status."""
    student_id: str = Field(..., description="Target student registration number")
    recommended_plan: Any = Field(..., description="Recommended 6-course schedule or strategic pathway summary")
    conflict_warnings: List[str] = Field(default_factory=list, description="Conflict warnings or violations detected (if any)")
    policy_citations: List[str] = Field(default_factory=list, description="Traceable university policy citations retrieved by Graph-RAG")
    system_health: Dict[str, str] = Field(..., description="Circuit breaker health status across all 5 agents")






