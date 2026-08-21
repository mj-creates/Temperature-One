"""
State Synthesizer Engine for Agent 4 - "The Background Check".
Evaluates raw DBMS records, enforces zero-tolerance hallucination, sanitizes data,
and produces the validated Student State JSON payload or standardized error protocol response.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Tuple

try:
    from .schemas import (
        AcademicState,
        EngagementState,
        StudentState,
        Agent4ErrorResponse,
        STUDENT_NOT_FOUND,
        DATABASE_CONNECTION_ERROR,
        INVALID_DBMS_PAYLOAD,
    )
    from .sanitizer import sanitize_dbms_record
except ImportError:
    from schemas import (
        AcademicState,
        EngagementState,
        StudentState,
        Agent4ErrorResponse,
        STUDENT_NOT_FOUND,
        DATABASE_CONNECTION_ERROR,
        INVALID_DBMS_PAYLOAD,
    )
    from sanitizer import sanitize_dbms_record


def format_error_response(error_code: str) -> str:
    """Returns raw valid JSON string for error protocol."""
    payload = {
        "status": "ERROR",
        "error_code": error_code,
        "state": None
    }
    return json.dumps(payload, indent=2)


def evaluate_academic_standing(gpa: Optional[float], explicit_standing: Optional[str] = None) -> Optional[str]:
    """
    Evaluates academic standing based strictly on DBMS data.
    If explicitly recorded in DBMS, that value is prioritized.
    Otherwise, evaluates objectively if GPA is available.
    """
    if explicit_standing is not None and str(explicit_standing).strip():
        return str(explicit_standing).strip().upper().replace(" ", "_")

    if gpa is None:
        return None

    # Standard scale evaluation (supporting 10-point scale used in university DB or standard 4.0 scale)
    if gpa > 4.0:
        # 10.0 Scale
        if gpa >= 8.5:
            return "HONORS"
        elif gpa >= 6.0:
            return "GOOD_STANDING"
        else:
            return "AT_RISK"
    else:
        # 4.0 Scale
        if gpa >= 3.7:
            return "HONORS"
        elif gpa >= 2.0:
            return "GOOD_STANDING"
        else:
            return "AT_RISK"


def generate_synthesis_summary(
    student_id: str,
    account_status: str,
    gpa: Optional[float],
    credits_earned: Optional[int],
    standing: Optional[str],
    attendance: Optional[float],
    last_activity: Optional[str],
    behavioral_flags: List[str],
    semester: Optional[int] = None,
) -> str:
    """
    Generates a precise, 2-sentence analytical summary based solely on DBMS facts.
    Maintains zero-tolerance hallucination and strict objectivity.
    """
    # Sentence 1: Academic Standing & Status
    sem_text = f" in Semester {semester}" if semester is not None else ""
    gpa_text = f"{gpa:.2f}" if gpa is not None else "unrecorded"
    credits_text = f"{credits_earned} credits earned/registered" if credits_earned is not None else "no credit data recorded"
    standing_text = standing.replace("_", " ") if standing else "unspecified standing"

    sentence_1 = (
        f"Student {student_id} is currently {account_status}{sem_text} with an academic evaluation of "
        f"{standing_text} (GPA: {gpa_text}, {credits_text})."
    )

    # Sentence 2: Engagement & Behavioral State
    att_text = f"{attendance:.1f}% attendance" if attendance is not None else "no attendance records"
    act_text = f"last activity recorded on {last_activity}" if last_activity else "no recent activity timestamp"
    flags_text = (
        f"{len(behavioral_flags)} behavioral flag(s) logged ({', '.join(behavioral_flags)})"
        if behavioral_flags
        else "zero behavioral flags on record"
    )

    sentence_2 = (
        f"Operational engagement indicates {att_text} with {act_text}, and {flags_text}."
    )

    return f"{sentence_1} {sentence_2}"


def synthesize_student_state(raw_record: Any) -> str:
    """
    Core function to synthesize a Student State JSON payload from a raw DBMS record.

    Args:
        raw_record: Raw dictionary, list, or JSON string from DBMS.

    Returns:
        Raw JSON string adhering to the required schema or error protocol.
    """
    # 1. Validate Input Payload Existence
    if raw_record is None:
        return format_error_response(STUDENT_NOT_FOUND)

    # Parse if string
    if isinstance(raw_record, str):
        content = raw_record.strip()
        if not content:
            return format_error_response(STUDENT_NOT_FOUND)
        try:
            raw_record = json.loads(content)
        except Exception:
            return format_error_response(INVALID_DBMS_PAYLOAD)

    if not isinstance(raw_record, dict):
        return format_error_response(INVALID_DBMS_PAYLOAD)

    if not raw_record:
        return format_error_response(STUDENT_NOT_FOUND)

    # 2. Check for explicit error flags from DB retrieval
    if raw_record.get("status") == "ERROR":
        err = raw_record.get("error_code", INVALID_DBMS_PAYLOAD)
        return format_error_response(err)

    # 3. Sanitize Payload (strip sensitive credentials, raw hashes, financial data)
    sanitized = sanitize_dbms_record(raw_record)

    # 4. Extract Student Identifier
    student_id = (
        sanitized.get("student_id")
        or sanitized.get("RegNo")
        or sanitized.get("reg_no")
        or sanitized.get("id")
    )
    if not student_id or not str(student_id).strip():
        return format_error_response(STUDENT_NOT_FOUND)
    student_id = str(student_id).strip()

    # 5. Extract Timestamp
    record_timestamp = (
        sanitized.get("record_timestamp")
        or sanitized.get("timestamp")
        or sanitized.get("last_updated")
        or sanitized.get("created_at")
    )
    if not record_timestamp:
        # Fallback to current UTC ISO timestamp for synthesis record
        record_timestamp = datetime.now(timezone.utc).isoformat()
    else:
        record_timestamp = str(record_timestamp)

    # 6. Extract Account Status
    account_status = (
        sanitized.get("account_status")
        or sanitized.get("status")
        or ("ACTIVE" if sanitized.get("Semester") or sanitized.get("semester") else "ACTIVE")
    )
    account_status = str(account_status).upper()

    # 7. Extract Academic State
    raw_gpa = (
        sanitized.get("current_gpa")
        if "current_gpa" in sanitized
        else sanitized.get("CGPA", sanitized.get("cgpa", sanitized.get("gpa")))
    )
    current_gpa: Optional[float] = None
    if raw_gpa is not None:
        try:
            current_gpa = float(raw_gpa)
        except (ValueError, TypeError):
            current_gpa = None

    # Credits Earned / Enrolled
    raw_credits = (
        sanitized.get("credits_earned")
        if "credits_earned" in sanitized
        else sanitized.get("credits", sanitized.get("total_credits"))
    )
    credits_earned: Optional[int] = None
    if raw_credits is not None:
        try:
            credits_earned = int(raw_credits)
        except (ValueError, TypeError):
            credits_earned = None
    elif "enrolled_subjects" in sanitized and isinstance(sanitized["enrolled_subjects"], list):
        # Calculate sum of credits if subjects list contains credit values
        subject_credits = [
            s.get("credits", s.get("Credits", 0))
            for s in sanitized["enrolled_subjects"]
            if isinstance(s, dict)
        ]
        if subject_credits and any(c > 0 for c in subject_credits):
            credits_earned = sum(subject_credits)

    # Academic Standing
    explicit_standing = (
        sanitized.get("academic_standing")
        or sanitized.get("standing")
        or (sanitized.get("academic_state", {}).get("academic_standing") if isinstance(sanitized.get("academic_state"), dict) else None)
    )
    academic_standing = evaluate_academic_standing(current_gpa, explicit_standing)

    academic_state = AcademicState(
        current_gpa=current_gpa,
        credits_earned=credits_earned,
        academic_standing=academic_standing,
    )

    # 8. Extract Engagement State
    raw_att = (
        sanitized.get("attendance_percentage")
        if "attendance_percentage" in sanitized
        else sanitized.get("attendance", sanitized.get("attendance_pct"))
    )
    attendance_percentage: Optional[float] = None
    if raw_att is not None:
        try:
            attendance_percentage = float(raw_att)
        except (ValueError, TypeError):
            attendance_percentage = None

    last_activity_date = (
        sanitized.get("last_activity_date")
        or sanitized.get("last_activity")
        or sanitized.get("last_active")
        or sanitized.get("EnrollmentDate")
        or sanitized.get("enrollment_date")
    )
    if last_activity_date is not None:
        last_activity_date = str(last_activity_date)

    raw_flags = (
        sanitized.get("behavioral_flags")
        if "behavioral_flags" in sanitized
        else sanitized.get("flags", sanitized.get("disciplinary_flags"))
    )
    behavioral_flags: List[str] = []
    if isinstance(raw_flags, list):
        behavioral_flags = [str(f) for f in raw_flags if f is not None]
    elif isinstance(raw_flags, str) and raw_flags.strip():
        behavioral_flags = [raw_flags.strip()]

    engagement_state = EngagementState(
        attendance_percentage=attendance_percentage,
        last_activity_date=last_activity_date,
        behavioral_flags=behavioral_flags,
    )

    # 9. Extract Semester for context
    semester_val = sanitized.get("Semester", sanitized.get("semester"))
    semester: Optional[int] = None
    if semester_val is not None:
        try:
            semester = int(semester_val)
        except (ValueError, TypeError):
            semester = None

    # 10. Generate Strict 2-Sentence Analytical Synthesis Summary
    synthesis_summary = generate_synthesis_summary(
        student_id=student_id,
        account_status=account_status,
        gpa=current_gpa,
        credits_earned=credits_earned,
        standing=academic_standing,
        attendance=attendance_percentage,
        last_activity=last_activity_date,
        behavioral_flags=behavioral_flags,
        semester=semester,
    )

    # 11. Construct StudentState
    student_state = StudentState(
        student_id=student_id,
        record_timestamp=record_timestamp,
        account_status=account_status,
        academic_state=academic_state,
        engagement_state=engagement_state,
        synthesis_summary=synthesis_summary,
    )

    # Return pure raw JSON string
    return json.dumps(student_state.model_dump(), indent=2)
