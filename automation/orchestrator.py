"""
Autonomous Multi-Agent Advising Orchestrator Pipeline.
======================================================
Acts as the central nervous system for the 5-Agent Academic Advising System:
  1. Agent 1: Nexus (Input & Goal Extractor)
  2. Agent 2: State (Background Check & Academic State Synthesizer)
  3. Agent 3: Codex (Graph-RAG Policy & University Rulebook Engine)
  4. Agent 4: Matrix (Graph Navigator & Topological Pathfinder)
  5. Agent 5: Vector (Career Trajectory & Strategic Momentum Planner)

Implements the Circuit Breaker Pattern, Graceful Degradation, State Accumulation,
and Async/Await microservice coordination optimized for FastAPI integration.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Configure module logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("advising_orchestrator")


# ===========================================================================
# 1. MOCKED / REAL-BACKED ASYNC AGENT MICROSERVICES
# ===========================================================================

async def call_nexus(student_id: str, user_query: Optional[str] = None) -> Dict[str, Any]:
    """Agent 1: Nexus (Input Parser & Goal Identifier).

    Parses the user query and student ID to identify the primary academic advising goal.

    Args:
        student_id: The unique student registration number (e.g., 'REG1001').
        user_query: Optional natural language input from the student.

    Returns:
        Dict[str, Any]: Structured goal and intent payload, or error dictionary.
    """
    logger.info(f"[Agent 1: Nexus] Ingesting input for student_id='{student_id}', query='{user_query}'")
    await asyncio.sleep(0.05)  # Simulate network latency

    if not student_id or not str(student_id).strip():
        return {"error": "INVALID_STUDENT_ID", "detail": "Student ID cannot be null or empty."}

    # Extract or infer career/academic goal
    default_goals = {
        "REG1001": "Machine Learning Engineer",
        "REG1002": "Cloud Systems Architect",
        "REG1003": "Full Stack Software Engineer",
        "REG1004": "Cybersecurity Analyst",
        "REG1005": "AI Researcher",
    }
    
    if user_query and user_query.strip():
        inferred_goal = user_query.strip()
    else:
        inferred_goal = default_goals.get(student_id, "Software Engineer")

    return {
        "status": "success",
        "agent": "Nexus",
        "student_id": student_id.strip(),
        "advising_goal": inferred_goal,
        "greeting": f"Hello {student_id}! Welcome to your academic advising session.",
        "intent": "DEGREE_AND_CAREER_PLANNING",
    }


async def call_state(student_id: str, nexus_data: Dict[str, Any]) -> Dict[str, Any]:
    """Agent 2: State (The Background Check).

    Inspects DBMS records, validates standing, and outputs zero-hallucination state.

    Args:
        student_id: The student registration number.
        nexus_data: Context dictionary produced by Nexus.

    Returns:
        Dict[str, Any]: Synthesized student academic and engagement state, or error.
    """
    logger.info(f"[Agent 2: State] Querying database record for student_id='{student_id}'")
    await asyncio.sleep(0.06)  # Simulate DBMS latency

    # Circuit breaker trigger for invalid/non-existent students
    if "INVALID" in student_id.upper() or student_id.startswith("ERR"):
        return {
            "error": "STUDENT_NOT_FOUND",
            "detail": f"Student with ID '{student_id}' does not exist in university records."
        }

    # Mock zero-hallucination verified state (matching Agent 4 schema)
    return {
        "status": "success",
        "agent": "State",
        "student_id": student_id,
        "account_status": "ACTIVE",
        "current_semester": 2,
        "academic_state": {
            "current_gpa": 8.45,
            "credits_earned": 20,
            "academic_standing": "GOOD_STANDING"
        },
        "completed_nodes": ["Sub_1_1", "Sub_1_2", "Sub_1_7", "Sub_1_10"],
        "engagement_state": {
            "attendance_percentage": 92.5,
            "last_activity_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "behavioral_flags": []
        },
        "synthesis_summary": f"Student {student_id} is in GOOD_STANDING with 20 credits earned and a CGPA of 8.45."
    }


async def call_codex(student_id: str, state_data: Dict[str, Any], goal: str) -> Dict[str, Any]:
    """Agent 3: Codex (Graph-RAG Policy & University Rules Engine).

    Retrieves degree constraints, prerequisite rules, and semester credit caps.

    Args:
        student_id: The student registration number.
        state_data: Verified academic state from Agent 2.
        goal: Target advising goal.

    Returns:
        Dict[str, Any]: Policy rules, prerequisite chains, and credit limits.
    """
    logger.info(f"[Agent 3: Codex] Retrieving university rules & curriculum policies for goal='{goal}'")
    await asyncio.sleep(0.04)  # Simulate Graph-RAG latency

    academic_standing = state_data.get("academic_state", {}).get("academic_standing", "GOOD_STANDING")
    max_credits = 15 if academic_standing == "PROBATION" else 20

    return {
        "status": "success",
        "agent": "Codex",
        "total_graduation_credits_required": 160,
        "max_credits_per_semester": max_credits,
        "degree_requirements": {
            "mandatory_subjects_per_term": 6,
            "target_term_credits": 20,
        },
        "policy_constraints": {
            "probation_credit_cap_enforced": academic_standing == "PROBATION",
            "prerequisite_waiver_allowed": False
        },
        "citation": "[Source: University_Academic_Catalog_Section_4_Degree_Progression]"
    }


async def call_matrix(
    student_id: str,
    state_data: Dict[str, Any],
    codex_data: Dict[str, Any],
    target_goal: str
) -> Dict[str, Any]:
    """Agent 4: Matrix (Graph Navigator & Pathfinder).

    Computes topologically sorted, conflict-free sequence to target milestone.

    Args:
        student_id: Student registration number.
        state_data: Academic state from Agent 2.
        codex_data: Policy and credit limits from Agent 3.
        target_goal: Target career/academic focus.

    Returns:
        Dict[str, Any]: Path sequence, bottlenecks, and logical proof.
    """
    logger.info(f"[Agent 4: Matrix] Calculating critical prerequisite path toward '{target_goal}'")
    await asyncio.sleep(0.07)  # Simulate graph traversal latency

    completed = state_data.get("completed_nodes", [])
    max_credits = codex_data.get("max_credits_per_semester", 20)

    # Simulated conflict-free sequence
    path_sequence = [
        {
            "step_number": 1,
            "step_label": "Semester 2 (Upcoming)",
            "nodes_to_complete": ["Sub_2_1", "Sub_2_3", "Sub_2_4", "Sub_2_9"],
            "step_total_credits_or_effort": 15.0
        },
        {
            "step_number": 2,
            "step_label": "Semester 3",
            "nodes_to_complete": ["Sub_3_1", "Sub_3_3", "Sub_3_5"],
            "step_total_credits_or_effort": 12.0
        },
        {
            "step_number": 3,
            "step_label": "Semester 4",
            "nodes_to_complete": ["Sub_4_1", "Sub_4_2"],
            "step_total_credits_or_effort": 8.0
        }
    ]

    return {
        "status": "success",
        "agent": "Matrix",
        "student_id": student_id,
        "target_milestone": target_goal,
        "path_status": "VALID",
        "total_steps_required": len(path_sequence),
        "path_sequence": path_sequence,
        "bottlenecks": ["Sub_2_1", "Sub_3_3"],
        "matrix_analysis": (
            "The computed 3-step trajectory establishes the shortest conflict-free topological sequence "
            f"to reach target milestones for {target_goal} with critical gateway at Sub_2_1. "
            f"Credit allocation is balanced under the {max_credits}-credit cap with zero cyclic dependencies."
        )
    }


async def call_vector(student_id: str, pipeline_context: Dict[str, Any]) -> Dict[str, Any]:
    """Agent 5: Vector (Future Scope & Career Trajectory Engine).

    Synthesizes the comprehensive pipeline context into a human-readable Strategic Plan.

    Args:
        student_id: Student registration number.
        pipeline_context: Complete aggregated context from Agents 1 through 4.

    Returns:
        Dict[str, Any]: Actionable Strategic Momentum Plan and career recommendations.
    """
    logger.info(f"[Agent 5: Vector] Generating Strategic Momentum Plan for student_id='{student_id}'")
    await asyncio.sleep(0.05)  # Simulate LLM synthesis latency

    goal = pipeline_context.get("nexus", {}).get("advising_goal", "Software Engineering")
    matrix_info = pipeline_context.get("matrix", {})
    state_info = pipeline_context.get("state", {})

    momentum_plan = (
        "**Strategic Momentum Plan:**\n"
        f"*   **Actionable Project:** Build an end-to-end distributed system applying Data Structures (Sub_2_1) "
        f"and Relational Databases (Sub_2_9) tailored for high-throughput {goal} pipelines.\n"
        f"*   **Internship/Career Target:** Target summer internship applications on LinkedIn and Internshala "
        f"for Junior {goal} roles aligning with Semester 3 coursework.\n"
        f"*   **Next-Level Milestone:** Complete Cloud Practitioner / Solutions Architect certification "
        "before entering Semester 4 to solidify cloud-native deployment competency."
    )

    return {
        "status": "success",
        "agent": "Vector",
        "student_id": student_id,
        "advising_goal": goal,
        "strategic_momentum_plan": momentum_plan,
        "executive_summary": (
            f"Student {student_id} is on a validated path to graduate in {goal}. "
            f"Academic standing is confirmed as {state_info.get('academic_state', {}).get('academic_standing', 'GOOD_STANDING')} "
            f"with {matrix_info.get('total_steps_required', 3)} structured academic terms remaining."
        )
    }


# ===========================================================================
# 2. CIRCUIT BREAKER & RESPONSE EVALUATION UTILITIES
# ===========================================================================

def is_agent_error(response: Any) -> bool:
    """Evaluates whether an agent's response indicates a failure or error.

    Args:
        response: The dictionary payload returned by an agent.

    Returns:
        bool: True if an error is detected, False otherwise.
    """
    if not isinstance(response, dict):
        return True
    if "error" in response and response["error"] is not None:
        return True
    if response.get("status") in ("ERROR", "failed", "PATH_UNREACHABLE", "GRAPH_ERROR"):
        return True
    return False


def build_circuit_breaker_failure(
    failed_agent_name: str,
    error_response: Any,
    student_id: str,
    pipeline_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Constructs a standardized, HTTP-friendly failure response when an agent halts.

    Args:
        failed_agent_name: Human-readable identifier of the failing agent.
        error_response: The raw response returned by the failed agent.
        student_id: The target student registration number.
        pipeline_context: The accumulated context prior to failure.

    Returns:
        Dict[str, Any]: Standardized error response for FastAPI / clients.
    """
    reason = "An unexpected error occurred during pipeline execution."
    if isinstance(error_response, dict):
        reason = (
            error_response.get("detail")
            or error_response.get("error")
            or error_response.get("reason")
            or str(error_response)
        )
    elif isinstance(error_response, str):
        reason = error_response

    logger.error(f"[Circuit Breaker Tripped] Pipeline halted at '{failed_agent_name}'. Reason: {reason}")

    return {
        "status": "failed",
        "failed_at": failed_agent_name,
        "reason": reason,
        "student_id": student_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "partial_context": pipeline_context,
    }


# ===========================================================================
# 3. END-TO-END ORCHESTRATOR PIPELINE
# ===========================================================================

async def run_advising(student_id: str, user_query: Optional[str] = None) -> Dict[str, Any]:
    """Orchestrates the end-to-end 5-agent AI academic advising pipeline.

    Executes the 5 specialized agents in strict sequence with state accumulation
    and circuit breaker error handling:
      1. Agent 1: Nexus (Input & Goal)
      2. Agent 2: State (Background Check)
      3. Agent 3: Codex (Policy Rules)
      4. Agent 4: Matrix (Prerequisite Pathfinder)
      5. Agent 5: Vector (Career & Momentum Plan)

    Args:
        student_id: Unique student registration ID (e.g. 'REG1001').
        user_query: Optional query/goal description from the student.

    Returns:
        Dict[str, Any]: Complete aggregated advising response, or graceful failure dictionary.
    """
    session_start = datetime.now(timezone.utc)
    pipeline_context: Dict[str, Any] = {
        "student_id": student_id,
        "user_query": user_query,
        "session_timestamp": session_start.isoformat(),
    }

    try:
        # -------------------------------------------------------------------
        # STEP 1: Agent 1 - Nexus (Input & Goal Parsing)
        # -------------------------------------------------------------------
        nexus_resp = await call_nexus(student_id=student_id, user_query=user_query)
        if is_agent_error(nexus_resp):
            return build_circuit_breaker_failure("Nexus Agent (Agent 1)", nexus_resp, student_id, pipeline_context)
        
        pipeline_context["nexus"] = nexus_resp
        target_goal = nexus_resp.get("advising_goal", "General Degree Progression")

        # -------------------------------------------------------------------
        # STEP 2: Agent 2 - State (Background Check & DBMS Verification)
        # -------------------------------------------------------------------
        state_resp = await call_state(student_id=student_id, nexus_data=nexus_resp)
        if is_agent_error(state_resp):
            return build_circuit_breaker_failure("State Agent (Agent 2)", state_resp, student_id, pipeline_context)
        
        pipeline_context["state"] = state_resp

        # -------------------------------------------------------------------
        # STEP 3: Agent 3 - Codex (Graph-RAG Policy & University Rules)
        # -------------------------------------------------------------------
        codex_resp = await call_codex(student_id=student_id, state_data=state_resp, goal=target_goal)
        if is_agent_error(codex_resp):
            return build_circuit_breaker_failure("Codex Agent (Agent 3)", codex_resp, student_id, pipeline_context)
        
        pipeline_context["codex"] = codex_resp

        # -------------------------------------------------------------------
        # STEP 4: Agent 4 - Matrix (Prerequisite Pathfinding & Scheduling)
        # -------------------------------------------------------------------
        matrix_resp = await call_matrix(
            student_id=student_id,
            state_data=state_resp,
            codex_data=codex_resp,
            target_goal=target_goal
        )
        if is_agent_error(matrix_resp):
            return build_circuit_breaker_failure("Matrix Agent (Agent 4)", matrix_resp, student_id, pipeline_context)
        
        pipeline_context["matrix"] = matrix_resp

        # -------------------------------------------------------------------
        # STEP 5: Agent 5 - Vector (Career & Momentum Synthesis)
        # -------------------------------------------------------------------
        vector_resp = await call_vector(student_id=student_id, pipeline_context=pipeline_context)
        if is_agent_error(vector_resp):
            return build_circuit_breaker_failure("Vector Agent (Agent 5)", vector_resp, student_id, pipeline_context)
        
        pipeline_context["vector"] = vector_resp

        # -------------------------------------------------------------------
        # FINAL SYNTHESIS: Unified HTTP-Ready Advising Payload
        # -------------------------------------------------------------------
        return {
            "status": "success",
            "student_id": student_id,
            "advising_goal": target_goal,
            "session_timestamp": session_start.isoformat(),
            "pipeline_context": pipeline_context,
            "final_plan": {
                "academic_status_summary": state_resp.get("synthesis_summary", ""),
                "semester_pathway": matrix_resp.get("path_sequence", []),
                "matrix_proof": matrix_resp.get("matrix_analysis", ""),
                "strategic_momentum_plan": vector_resp.get("strategic_momentum_plan", ""),
                "executive_summary": vector_resp.get("executive_summary", ""),
            }
        }

    except Exception as exc:
        # Ultimate fallback barrier: prevent unhandled exceptions from crashing FastAPI
        logger.exception(f"[FATAL] Uncaught exception in orchestrator pipeline: {exc}")
        return build_circuit_breaker_failure(
            failed_agent_name="Pipeline Engine",
            error_response={"error": "INTERNAL_ORCHESTRATOR_ERROR", "detail": str(exc)},
            student_id=student_id,
            pipeline_context=pipeline_context
        )


# ===========================================================================
# 4. CLI DEMONSTRATION HARNESS
# ===========================================================================

async def main():
    """Runs automated verification demonstrations for successful and failing pipeline cases."""
    print("=" * 80)
    print(" ANTI GRAVITY - 5-AGENT END-TO-END ORCHESTRATOR DEMO")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # TEST 1: Successful Pipeline Execution
    # -----------------------------------------------------------------------
    print("\n[TEST 1] Executing Full Successful Advising Pipeline (REG1001, 'AI Researcher')...")
    result_success = await run_advising(student_id="REG1001", user_query="AI Researcher")
    print(json.dumps(result_success, indent=2))
    assert result_success["status"] == "success"
    assert "pipeline_context" in result_success
    assert "final_plan" in result_success
    print(">>> [TEST 1 RESULT] PASSED - All 5 agents completed successfully.")

    # -----------------------------------------------------------------------
    # TEST 2: Circuit Breaker Failure Simulation (Non-Existent Student)
    # -----------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("[TEST 2] Executing Pipeline with Invalid Student ID (Circuit Breaker Trigger)...")
    result_failure = await run_advising(student_id="INVALID_STUDENT_9999", user_query="Data Scientist")
    print(json.dumps(result_failure, indent=2))
    assert result_failure["status"] == "failed"
    assert result_failure["failed_at"] == "State Agent (Agent 2)"
    assert result_failure["reason"] == "Student with ID 'INVALID_STUDENT_9999' does not exist in university records."
    print(">>> [TEST 2 RESULT] PASSED - Circuit Breaker halted execution gracefully.")

    print("\n" + "=" * 80)
    print(" ALL ORCHESTRATOR DEMONSTRATION TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
