"""
Agent Core Entrypoint & CLI Runner.
Demonstrates Agent 4 ("The Background Check") operations, tests schema compliance,
and runs evaluations against local SQLite DBMS and mock payloads.
"""

import sys
import json
from pathlib import Path

# Ensure directory is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from schemas import (
    STUDENT_NOT_FOUND,
    DATABASE_CONNECTION_ERROR,
    INVALID_DBMS_PAYLOAD,
)
from sanitizer import sanitize_dbms_record
from synthesizer import synthesize_student_state
from agent_4_background_check import Agent4BackgroundCheck, run_agent_4


def run_demo():
    print("=" * 80)
    print(" ANTI GRAVITY - AGENT 4: THE BACKGROUND CHECK (STATE SYNTHESIZER)")
    print("=" * 80)

    agent = Agent4BackgroundCheck()

    # Scenario 1: Inspect valid student from SQLite DBMS
    sample_reg_no = "REG1001"
    print(f"\n[SCENARIO 1] Querying DBMS for student ID: {sample_reg_no}")
    result_json = agent.inspect_student_id(sample_reg_no)
    print(result_json)

    # Validate output is valid JSON
    parsed = json.loads(result_json)
    assert parsed["student_id"] == sample_reg_no
    assert "academic_state" in parsed
    assert "engagement_state" in parsed
    assert "synthesis_summary" in parsed
    print("  -> Schema Validation: PASSED")

    # Scenario 2: Inspect raw DBMS payload with sensitive data (Sanitization test)
    raw_payload_with_credentials = {
        "student_id": "REG9999",
        "record_timestamp": "2026-08-21T10:00:00Z",
        "account_status": "PROBATION",
        "current_gpa": 5.40,
        "credits_earned": 38,
        "attendance_percentage": 68.5,
        "last_activity_date": "2026-08-20",
        "behavioral_flags": ["ATTENDANCE_WARNING", "ACADEMIC_PROBATION"],
        # Sensitive credentials that MUST be sanitized:
        "password_hash": "$2b$12$e89sf890sdfljk...",
        "api_key": "sk_live_secret123456",
        "bank_account": "9876543210",
        "credit_card": "4111-2222-3333-4444",
    }
    print("\n[SCENARIO 2] Inspecting payload containing sensitive credentials (Sanitization Test):")
    sanitized_output = agent.inspect_raw_payload(raw_payload_with_credentials)
    print(sanitized_output)
    assert "password_hash" not in sanitized_output
    assert "api_key" not in sanitized_output
    assert "bank_account" not in sanitized_output
    assert "credit_card" not in sanitized_output
    print("  -> Security & Sanitization Check: PASSED (Sensitive fields stripped)")

    # Scenario 3: Non-existent student (Error Protocol test)
    print("\n[SCENARIO 3] Querying non-existent student (STUDENT_NOT_FOUND):")
    not_found_output = agent.inspect_student_id("NON_EXISTENT_ID")
    print(not_found_output)
    err_parsed = json.loads(not_found_output)
    assert err_parsed["status"] == "ERROR"
    assert err_parsed["error_code"] == STUDENT_NOT_FOUND
    assert err_parsed["state"] is None
    print("  -> Error Protocol Check: PASSED")

    # Scenario 4: Malformed payload (Error Protocol test)
    print("\n[SCENARIO 4] Inspecting malformed payload (INVALID_DBMS_PAYLOAD):")
    malformed_output = agent.inspect_raw_payload("NOT_A_VALID_JSON_STRING_OR_DICT")
    print(malformed_output)
    err_malformed = json.loads(malformed_output)
    assert err_malformed["status"] == "ERROR"
    assert err_malformed["error_code"] == INVALID_DBMS_PAYLOAD
    assert err_malformed["state"] is None
    print("  -> Malformed Payload Protocol Check: PASSED")

    # Scenario 5: Missing / NULL fields (Zero-Hallucination test)
    minimal_record = {
        "student_id": "REG8888",
        "current_gpa": None,
        "credits_earned": None,
        "attendance_percentage": None,
    }
    print("\n[SCENARIO 5] Evaluating record with NULL/missing fields (Zero-Hallucination Test):")
    zero_hal_output = agent.inspect_raw_payload(minimal_record)
    print(zero_hal_output)
    zh_parsed = json.loads(zero_hal_output)
    assert zh_parsed["academic_state"]["current_gpa"] is None
    assert zh_parsed["academic_state"]["credits_earned"] is None
    assert zh_parsed["engagement_state"]["attendance_percentage"] is None
    assert zh_parsed["engagement_state"]["behavioral_flags"] == []
    print("  -> Zero-Tolerance Hallucination Check: PASSED (Explicitly null / empty lists)")

    print("\n" + "=" * 80)
    print(" ALL AGENT 4 VERIFICATION SCENARIOS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(run_agent_4(target))
    else:
        run_demo()
