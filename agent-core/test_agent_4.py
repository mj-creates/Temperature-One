"""
Unit Tests for Agent 4 - "The Background Check" (State Synthesizer).
"""

import sys
import json
import sqlite3
import unittest
from pathlib import Path

# Add current directory to path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from schemas import (
    AcademicState,
    EngagementState,
    StudentState,
    STUDENT_NOT_FOUND,
    DATABASE_CONNECTION_ERROR,
    INVALID_DBMS_PAYLOAD,
)
from sanitizer import sanitize_dbms_record, is_sensitive_key
from synthesizer import (
    synthesize_student_state,
    format_error_response,
    evaluate_academic_standing,
)
from agent_4_background_check import Agent4BackgroundCheck


class TestAgent4Sanitization(unittest.TestCase):
    def test_strip_sensitive_fields(self):
        raw = {
            "student_id": "REG1001",
            "password": "secret_password",
            "password_hash": "argon2id$...",
            "api_key": "sk-12345",
            "credit_card": "4000-1234-5678-9010",
            "bank_account": "123456789",
            "nested": {
                "auth_token": "token123",
                "ssn": "000-00-0000",
                "clean_field": "visible_value"
            }
        }
        sanitized = sanitize_dbms_record(raw)
        self.assertNotIn("password", sanitized)
        self.assertNotIn("password_hash", sanitized)
        self.assertNotIn("api_key", sanitized)
        self.assertNotIn("credit_card", sanitized)
        self.assertNotIn("bank_account", sanitized)
        self.assertNotIn("auth_token", sanitized["nested"])
        self.assertNotIn("ssn", sanitized["nested"])
        self.assertEqual(sanitized["nested"]["clean_field"], "visible_value")


class TestAgent4Synthesizer(unittest.TestCase):
    def test_zero_hallucination_null_handling(self):
        raw = {
            "student_id": "REG1001",
            "current_gpa": None,
            "credits_earned": None,
            "attendance_percentage": None,
            "behavioral_flags": None,
        }
        res_json = synthesize_student_state(raw)
        data = json.loads(res_json)
        self.assertEqual(data["student_id"], "REG1001")
        self.assertIsNone(data["academic_state"]["current_gpa"])
        self.assertIsNone(data["academic_state"]["credits_earned"])
        self.assertIsNone(data["academic_state"]["academic_standing"])
        self.assertIsNone(data["engagement_state"]["attendance_percentage"])
        self.assertEqual(data["engagement_state"]["behavioral_flags"], [])

    def test_academic_standing_evaluation(self):
        self.assertEqual(evaluate_academic_standing(9.2), "HONORS")
        self.assertEqual(evaluate_academic_standing(7.5), "GOOD_STANDING")
        self.assertEqual(evaluate_academic_standing(5.2), "AT_RISK")
        self.assertEqual(evaluate_academic_standing(3.9), "HONORS")
        self.assertEqual(evaluate_academic_standing(3.2), "GOOD_STANDING")
        self.assertEqual(evaluate_academic_standing(1.8), "AT_RISK")
        self.assertEqual(evaluate_academic_standing(None), None)
        self.assertEqual(evaluate_academic_standing(7.0, "PROBATION"), "PROBATION")

    def test_error_protocols(self):
        # Empty payload
        res = json.loads(synthesize_student_state(None))
        self.assertEqual(res["status"], "ERROR")
        self.assertEqual(res["error_code"], STUDENT_NOT_FOUND)
        self.assertIsNone(res["state"])

        # Malformed payload
        res = json.loads(synthesize_student_state("Not valid json"))
        self.assertEqual(res["status"], "ERROR")
        self.assertEqual(res["error_code"], INVALID_DBMS_PAYLOAD)
        self.assertIsNone(res["state"])


class TestAgent4DatabaseIntegration(unittest.TestCase):
    def setUp(self):
        self.agent = Agent4BackgroundCheck()

    def test_query_existing_student_from_db(self):
        # Test student query if DB exists
        if self.agent.db_path.exists():
            res_json = self.agent.inspect_student_id("REG1001")
            data = json.loads(res_json)
            self.assertEqual(data["student_id"], "REG1001")
            self.assertIn("academic_state", data)
            self.assertIn("engagement_state", data)
            self.assertIn("synthesis_summary", data)

    def test_query_nonexistent_student(self):
        res_json = self.agent.inspect_student_id("NON_EXISTENT_STUDENT")
        data = json.loads(res_json)
        self.assertEqual(data["status"], "ERROR")
        self.assertEqual(data["error_code"], STUDENT_NOT_FOUND)
        self.assertIsNone(data["state"])

    def test_db_connection_error(self):
        invalid_agent = Agent4BackgroundCheck(db_path=Path("non_existent_dir/db.sqlite"))
        res_json = invalid_agent.inspect_student_id("REG1001")
        data = json.loads(res_json)
        self.assertEqual(data["status"], "ERROR")
        self.assertEqual(data["error_code"], DATABASE_CONNECTION_ERROR)
        self.assertIsNone(data["state"])


if __name__ == "__main__":
    unittest.main()
