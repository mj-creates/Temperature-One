"""
Agent 4 - "The Background Check" (State Synthesizer)
Autonomous agent implementation for inspecting raw student records from the DBMS
and producing validated, structured Student State JSON outputs.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Union, Tuple

try:
    from .agent_schemas import (
        StudentState,
        Agent4ErrorResponse,
        STUDENT_NOT_FOUND,
        DATABASE_CONNECTION_ERROR,
        INVALID_DBMS_PAYLOAD,
    )
    from .synthesizer import synthesize_student_state, format_error_response
    from .prompts import SYSTEM_PROMPT, get_agent4_prompt, build_evaluation_prompt
except ImportError:
    from agent_schemas import (
        StudentState,
        Agent4ErrorResponse,
        STUDENT_NOT_FOUND,
        DATABASE_CONNECTION_ERROR,
        INVALID_DBMS_PAYLOAD,
    )
    from synthesizer import synthesize_student_state, format_error_response
    from prompts import SYSTEM_PROMPT, get_agent4_prompt, build_evaluation_prompt

# Default backend database path
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "university.db"


class Agent4BackgroundCheck:
    """
    Agent 4: The Background Check (State Synthesizer).
    
    Inspects raw student records from the DBMS, evaluates operational and
    academic standing with zero-tolerance hallucination, and outputs
    validated Student State JSON.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.system_prompt = SYSTEM_PROMPT

    def _get_read_only_connection(self, custom_path: Optional[Path] = None) -> sqlite3.Connection:
        """
        Creates a strictly read-only SQLite connection to prevent any accidental mutations.
        """
        target_path = custom_path or self.db_path
        if not target_path.exists():
            raise FileNotFoundError(f"Database file does not exist at {target_path}")

        # Use SQLite URI read-only mode if supported, with fallback
        try:
            db_uri = f"file:{target_path.as_posix()}?mode=ro"
            conn = sqlite3.connect(db_uri, uri=True)
        except Exception:
            conn = sqlite3.connect(str(target_path))

        conn.row_factory = sqlite3.Row
        return conn

    def fetch_raw_student_from_db(self, student_id: str, custom_db_path: Optional[Path] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieves the raw student and enrolled subjects record from the DBMS.
        Returns (raw_record_dict, error_code_if_any).
        """
        if not student_id or not str(student_id).strip():
            return None, STUDENT_NOT_FOUND

        student_id = str(student_id).strip()

        try:
            conn = self._get_read_only_connection(custom_db_path)
        except Exception:
            return None, DATABASE_CONNECTION_ERROR

        try:
            cursor = conn.cursor()

            # Query student profile
            cursor.execute(
                "SELECT RegNo, StudentName, Semester, CGPA, Goal FROM Students WHERE RegNo = ? COLLATE NOCASE;",
                (student_id,)
            )
            student_row = cursor.fetchone()

            if not student_row:
                conn.close()
                return None, STUDENT_NOT_FOUND

            student_dict = dict(student_row)

            # Query enrolled subjects and calculate total credits & enrollment date
            cursor.execute("""
                SELECT 
                    sub.SubjectID, 
                    sub.SubjectName, 
                    sub.Credits, 
                    ss.EnrollmentDate
                FROM Student_Subjects ss
                JOIN Subjects sub ON ss.SubjectID = sub.SubjectID
                WHERE ss.RegNo = ?
                ORDER BY sub.SubjectID;
            """, (student_id,))
            subject_rows = cursor.fetchall()

            enrolled_subjects = [dict(row) for row in subject_rows]
            total_credits = sum(s.get("Credits", 0) for s in enrolled_subjects) if enrolled_subjects else None
            last_activity = enrolled_subjects[0].get("EnrollmentDate") if enrolled_subjects else None

            # Construct raw DBMS payload representing database state
            raw_dbms_record = {
                "student_id": student_dict.get("RegNo"),
                "student_name": student_dict.get("StudentName"),
                "semester": student_dict.get("Semester"),
                "current_gpa": student_dict.get("CGPA"),
                "career_goal": student_dict.get("Goal"),
                "credits_earned": total_credits,
                "account_status": "ACTIVE",
                "enrolled_subjects": enrolled_subjects,
                "last_activity_date": last_activity,
                "attendance_percentage": None,  # Explicitly unrecorded in this table schema
                "behavioral_flags": [],        # Explicitly unrecorded
            }

            conn.close()
            return raw_dbms_record, None

        except sqlite3.Error:
            try:
                conn.close()
            except Exception:
                pass
            return None, DATABASE_CONNECTION_ERROR
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            return None, INVALID_DBMS_PAYLOAD

    def inspect_student_id(self, student_id: str, custom_db_path: Optional[Path] = None) -> str:
        """
        Fetches student record from DBMS and synthesizes the validated Student State JSON.
        """
        raw_record, err_code = self.fetch_raw_student_from_db(student_id, custom_db_path)
        if err_code:
            return format_error_response(err_code)
        return synthesize_student_state(raw_record)

    def inspect_raw_payload(self, raw_payload: Any) -> str:
        """
        Evaluates any provided raw DBMS payload (dict, JSON string, or object) and returns Student State JSON.
        """
        return synthesize_student_state(raw_payload)

    def process_student(self, reg_number: str, name: Optional[str] = None, goal: Optional[str] = None) -> str:
        """
        Pipeline hand-off receiver method for upstream agents (e.g., Nexus Agent 1).
        Inspects the student record in DBMS and outputs validated Student State JSON.
        """
        return self.inspect_student_id(reg_number)

    def run(self, input_target: Any) -> str:
        """
        Unified inspection runner for Agent 4.
        Accepts a student identifier string, raw DBMS dict, or JSON string.
        """
        if isinstance(input_target, dict):
            return self.inspect_raw_payload(input_target)
        elif isinstance(input_target, str):
            trimmed = input_target.strip()
            # If JSON object string
            if trimmed.startswith("{") and trimmed.endswith("}"):
                return self.inspect_raw_payload(trimmed)
            else:
                # Treat as Student ID / RegNo
                return self.inspect_student_id(trimmed)
        else:
            return format_error_response(INVALID_DBMS_PAYLOAD)


# Convenient functional wrapper
def run_agent_4(input_target: Any, db_path: Optional[Path] = None) -> str:
    """Convenience functional wrapper for Agent 4 Background Check."""
    agent = Agent4BackgroundCheck(db_path=db_path)
    return agent.run(input_target)
