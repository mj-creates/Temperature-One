"""
Backend Schema Definitions & Exports
====================================
Standardized Pydantic schemas for students, subjects, degree requirements,
faculty petitions, and multi-agent advising session payloads.
"""

from backend.domain_schemas import (
    StudentSummary,
    StudentDetail,
    SubjectItem,
    SubjectsBySemesterResponse,
    DegreeRuleItem,
    DegreeRequirementsResponse,
    AgentBackgroundCheckResponse,
    AdvisingSessionRequest,
    AdvisingSessionResponse,
    ConflictCheckRequest,
    ConflictCheckResponse,
    ConflictItem,
    WaiverCreateRequest,
    WaiverApprovalRequest,
    WaiverResponse,
)

__all__ = [
    "StudentSummary",
    "StudentDetail",
    "SubjectItem",
    "SubjectsBySemesterResponse",
    "DegreeRuleItem",
    "DegreeRequirementsResponse",
    "AgentBackgroundCheckResponse",
    "AdvisingSessionRequest",
    "AdvisingSessionResponse",
    "ConflictCheckRequest",
    "ConflictCheckResponse",
    "ConflictItem",
    "WaiverCreateRequest",
    "WaiverApprovalRequest",
    "WaiverResponse",
]
