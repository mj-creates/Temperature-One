"""
Agent Core Entrypoint & CLI Runner.
Demonstrates multi-agent operations, tests schema compliance, and runs evaluations:
- Agent 1: Nexus (Front Desk / Orchestration Hub)
- Agent 2: The Matrix (Graph Navigator & Pathfinder)
- Agent 4: The Background Check (State Synthesizer)
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
    STATUS_VALID,
    STATUS_PATH_UNREACHABLE,
    STATUS_GRAPH_ERROR,
    STATUS_ALREADY_ACHIEVED,
    ERROR_MISSING_CRITICAL_NODE,
    ERROR_CYCLIC_DEPENDENCY,
)
from sanitizer import sanitize_dbms_record
from synthesizer import synthesize_student_state
from agent_4_background_check import Agent4BackgroundCheck, run_agent_4
from agent_matrix import MatrixAgent, run_matrix
from nexus import NexusAgent


def run_agent_4_demos(agent_4: Agent4BackgroundCheck):
    print("\n" + "=" * 80)
    print(" [1] AGENT 4: THE BACKGROUND CHECK (STATE SYNTHESIZER)")
    print("=" * 80)

    # Scenario 1: Inspect valid student from SQLite DBMS
    sample_reg_no = "REG1001"
    print(f"\n>>> Scenario 1.1: Querying DBMS for student ID: {sample_reg_no}")
    result_json = agent_4.inspect_student_id(sample_reg_no)
    print(result_json)
    parsed = json.loads(result_json)
    assert parsed["student_id"] == sample_reg_no
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
        "password_hash": "$2b$12$e89sf890sdfljk...",
        "api_key": "sk_live_secret123456",
        "bank_account": "9876543210",
        "credit_card": "4111-2222-3333-4444",
    }
    print("\n>>> Scenario 1.2: Inspecting payload containing sensitive credentials (Sanitization Test):")
    sanitized_output = agent_4.inspect_raw_payload(raw_payload_with_credentials)
    print(sanitized_output)
    assert "password_hash" not in sanitized_output
    assert "api_key" not in sanitized_output
    print("  -> Security & Sanitization Check: PASSED")

    # Scenario 3: Non-existent student (Error Protocol test)
    print("\n>>> Scenario 1.3: Querying non-existent student (STUDENT_NOT_FOUND):")
    not_found_output = agent_4.inspect_student_id("NON_EXISTENT_ID")
    print(not_found_output)
    err_parsed = json.loads(not_found_output)
    assert err_parsed["status"] == "ERROR"
    assert err_parsed["error_code"] == STUDENT_NOT_FOUND
    print("  -> Error Protocol Check: PASSED")


def run_matrix_demos(matrix_agent: MatrixAgent):
    print("\n" + "=" * 80)
    print(" [2] AGENT 2: THE MATRIX (GRAPH NAVIGATOR & PATHFINDER)")
    print("=" * 80)

    # Scenario 1: Valid Path Generation for Advanced Target
    target_node = "Sub_4_2"  # Deep Learning
    print(f"\n>>> Scenario 2.1: Computing optimal path to target course: {target_node}")
    path_json = matrix_agent.compute_path("REG1001", target_node, completed_nodes=[])
    print(path_json)
    parsed = json.loads(path_json)
    assert parsed["path_status"] == STATUS_VALID
    assert parsed["total_steps_required"] >= 2
    print("  -> Pathfinding & Topological Scheduling: PASSED")

    # Scenario 2: State Awareness (Student already completed prerequisites)
    print(f"\n>>> Scenario 2.2: State-aware path with completed prerequisite nodes:")
    completed = ["Sub_1_1", "Sub_1_2", "Sub_2_1", "Sub_2_3", "Sub_2_5", "Sub_3_3", "Sub_3_5"]
    state_aware_json = matrix_agent.compute_path("REG1001", target_node, completed_nodes=completed)
    print(state_aware_json)
    sa_parsed = json.loads(state_aware_json)
    assert sa_parsed["path_status"] == STATUS_VALID
    assert sa_parsed["total_steps_required"] == 2  # Sub_4_1 -> Sub_4_2
    print("  -> State Awareness & Load Optimization: PASSED")

    # Scenario 3: Target Already Achieved Impasse
    print(f"\n>>> Scenario 2.3: Target already completed by student (ALREADY_ACHIEVED):")
    already_done_json = matrix_agent.compute_path("REG1001", target_node, completed_nodes=[target_node])
    print(already_done_json)
    ad_parsed = json.loads(already_done_json)
    assert ad_parsed["status"] == STATUS_ALREADY_ACHIEVED
    print("  -> Already Achieved Protocol: PASSED")

    # Scenario 4: Missing Critical Node Impasse
    print(f"\n>>> Scenario 2.4: Unreachable path with missing prerequisite (PATH_UNREACHABLE):")
    custom_broken_nodes = [{"node_id": "Target_Course", "prerequisites": ["MISSING_COURSE_X"]}]
    unreachable_json = matrix_agent.compute_path("REG1001", "Target_Course", custom_graph_nodes=custom_broken_nodes)
    print(unreachable_json)
    un_parsed = json.loads(unreachable_json)
    assert un_parsed["status"] == STATUS_PATH_UNREACHABLE
    assert un_parsed["error"] == ERROR_MISSING_CRITICAL_NODE
    print("  -> Missing Critical Node Protocol: PASSED")

    # Scenario 5: Cyclic Dependency Impasse
    print(f"\n>>> Scenario 2.5: Circular prerequisite graph (GRAPH_ERROR CYCLIC_DEPENDENCY):")
    custom_cycle_nodes = [
        {"node_id": "A", "prerequisites": ["B"]},
        {"node_id": "B", "prerequisites": ["A"]},
        {"node_id": "Goal", "prerequisites": ["A"]}
    ]
    cycle_json = matrix_agent.compute_path("REG1001", "Goal", custom_graph_nodes=custom_cycle_nodes)
    print(cycle_json)
    cyc_parsed = json.loads(cycle_json)
    assert cyc_parsed["status"] == STATUS_GRAPH_ERROR
    assert cyc_parsed["error"] == ERROR_CYCLIC_DEPENDENCY
    print("  -> Cyclic Dependency Detection: PASSED")


def run_all_demos():
    print("=" * 80)
    print(" ANTI GRAVITY AUTONOMOUS PIPELINE - MULTI-AGENT VERIFICATION HARNESS")
    print("=" * 80)

    agent_4 = Agent4BackgroundCheck()
    matrix_agent = MatrixAgent()

    run_agent_4_demos(agent_4)
    run_matrix_demos(matrix_agent)

    print("\n" + "=" * 80)
    print(" ALL AGENT SCENARIOS COMPLETED SUCCESSFULLY WITH ZERO ERRORS")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--matrix":
        print(run_matrix(student_id="REG1001", target_node=sys.argv[2]))
    elif len(sys.argv) > 1:
        print(run_agent_4(sys.argv[1]))
    else:
        run_all_demos()
