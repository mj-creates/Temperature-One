# Agent Core: System Architecture & Agent 4

## Anti Gravity Autonomous Pipeline

This package houses the autonomous agent logic, synthesis engines, and schemas for the Anti Gravity pipeline.

---

## Agent 4: "The Background Check" (State Synthesizer)

### 1. Core Mission
Agent 4 inspects raw student records from the backend Database Management System (DBMS), evaluates the student's operational and academic standing, and outputs a validated, structured "Student State" JSON payload for downstream agents.

### 2. Operational Guardrails
- **Zero-Tolerance Hallucination**: Base evaluations exclusively on raw DBMS data. If a field is `NULL` or missing, output `null` or `[]`.
- **Read-Only Execution**: Passive inspection agent; never issues or suggests database mutations.
- **Security & Sanitization**: Automatically scrubs credentials, raw password hashes, API tokens, and financial data.
- **Objectivity**: Strict, analytical tone without emotional language or moral judgment.

### 3. Error Protocols
- **Empty Record / Not Found**: `{"status": "ERROR", "error_code": "STUDENT_NOT_FOUND", "state": null}`
- **DB Connection Failure**: `{"status": "ERROR", "error_code": "DATABASE_CONNECTION_ERROR", "state": null}`
- **Malformed Data**: `{"status": "ERROR", "error_code": "INVALID_DBMS_PAYLOAD", "state": null}`

### 4. Output JSON Schema
```json
{
  "student_id": "string",
  "record_timestamp": "string (ISO-8601 or DBMS timestamp)",
  "account_status": "string (e.g., ACTIVE, INACTIVE, SUSPENDED, PROBATION)",
  "academic_state": {
    "current_gpa": "number or null",
    "credits_earned": "integer or null",
    "academic_standing": "string (e.g., GOOD_STANDING, AT_RISK, HONORS)"
  },
  "engagement_state": {
    "attendance_percentage": "number or null",
    "last_activity_date": "string or null",
    "behavioral_flags": ["array of strings"]
  },
  "synthesis_summary": "A precise, 2-sentence analytical summary of the student's current state based solely on DBMS facts."
}
```

---

## Quick Usage

### Programmatic API
```python
from agent_core import Agent4BackgroundCheck, run_agent_4

# Query from SQLite database
agent = Agent4BackgroundCheck()
student_state_json = agent.inspect_student_id("REG1001")
print(student_state_json)

# Or evaluate raw DBMS payload
raw_dbms_record = {
    "student_id": "REG1002",
    "CGPA": 8.75,
    "credits_earned": 24,
    "attendance_percentage": 94.0,
    "last_activity_date": "2026-08-21",
    "behavioral_flags": []
}
result_json = agent.inspect_raw_payload(raw_dbms_record)
print(result_json)
```

### CLI Execution
```bash
# Run demo test scenarios
python agent-core/main.py

# Query a specific student ID from the local SQLite DB
python agent-core/main.py REG1001

# Run unit tests
python -m unittest discover -s agent-core
```
