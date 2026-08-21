"""
Agent Core Package - Anti Gravity Autonomous Pipeline
"""

from .schemas import (
    AcademicState,
    EngagementState,
    StudentState,
    Agent4ErrorResponse,
    STUDENT_NOT_FOUND,
    DATABASE_CONNECTION_ERROR,
    INVALID_DBMS_PAYLOAD,
    PathStep,
    MatrixPathResponse,
    MatrixErrorResponse,
    STATUS_VALID,
    STATUS_PATH_UNREACHABLE,
    STATUS_GRAPH_ERROR,
    STATUS_ALREADY_ACHIEVED,
    ERROR_MISSING_CRITICAL_NODE,
    ERROR_CYCLIC_DEPENDENCY,
)
from .sanitizer import sanitize_dbms_record, is_sensitive_key
from .synthesizer import (
    synthesize_student_state,
    format_error_response,
    evaluate_academic_standing,
    generate_synthesis_summary,
)
from .prompts import (
    SYSTEM_PROMPT,
    AGENT_4_SYSTEM_PROMPT,
    MATRIX_SYSTEM_PROMPT,
    get_agent4_prompt,
    get_matrix_prompt,
    build_evaluation_prompt,
    build_matrix_prompt,
)
from .agent_4_background_check import Agent4BackgroundCheck, run_agent_4
from .nexus import NexusAgent
from .matrix_graph import GraphNode, PrerequisiteGraph
from .agent_matrix import MatrixAgent, run_matrix
from .agent_3_vector import Agent3Vector

__all__ = [
    # Agents
    "NexusAgent",
    "MatrixAgent",
    "Agent3Vector",
    "Agent4BackgroundCheck",
    "run_agent_4",
    "run_matrix",
    # Agent 4 Schemas & Functions
    "StudentState",
    "AcademicState",
    "EngagementState",
    "Agent4ErrorResponse",
    "synthesize_student_state",
    "format_error_response",
    "evaluate_academic_standing",
    "generate_synthesis_summary",
    "sanitize_dbms_record",
    "is_sensitive_key",
    "STUDENT_NOT_FOUND",
    "DATABASE_CONNECTION_ERROR",
    "INVALID_DBMS_PAYLOAD",
    # Matrix Schemas & Graph
    "PathStep",
    "MatrixPathResponse",
    "MatrixErrorResponse",
    "GraphNode",
    "PrerequisiteGraph",
    "STATUS_VALID",
    "STATUS_PATH_UNREACHABLE",
    "STATUS_GRAPH_ERROR",
    "STATUS_ALREADY_ACHIEVED",
    "ERROR_MISSING_CRITICAL_NODE",
    "ERROR_CYCLIC_DEPENDENCY",
    # Prompts
    "SYSTEM_PROMPT",
    "AGENT_4_SYSTEM_PROMPT",
    "MATRIX_SYSTEM_PROMPT",
    "get_agent4_prompt",
    "get_matrix_prompt",
    "build_evaluation_prompt",
    "build_matrix_prompt",
]
