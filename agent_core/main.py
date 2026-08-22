"""
Agent Core Multi-Agent Pipeline Verification Harness
====================================================
Tests and demonstrates all 6 autonomous agents:
- Agent 1: Nexus (Supervisor & Pipeline Hub)
- Agent 2: The Matrix (Graph Navigator & Pathfinder)
- Agent 3: Vector (Strategic Career Velocity Engine)
- Agent 4: The Background Check (State Synthesizer)
- Agent 5: Codex (Graph-RAG Policy & Citation Engine)
- Agent 6: Sentinel (Formal Constraint & Faculty Verifier)
"""

import json
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from agent_schemas import (
    STUDENT_NOT_FOUND,
    STATUS_VALID,
)
from agent_4_background_check import Agent4BackgroundCheck
from agent_matrix import MatrixAgent
from agent_3_vector import Agent3Vector
from agent_codex_rag import CodexGraphRAGAgent
from agent_sentinel_verifier import SentinelVerifierAgent
from nexus import NexusAgent


def test_full_pipeline():
    print("=" * 80)
    print(" ANTI GRAVITY DECENTRALIZED MULTI-AGENT PLATFORM - VERIFICATION TEST")
    print("=" * 80)

    sample_id = "REG1001"
    nexus = NexusAgent()

    print(f"\n>>> Running End-to-End Multi-Agent Advising Pipeline for Student: {sample_id}")
    session = nexus.run_full_advising_pipeline(sample_id)

    print(f"\n[Session ID]: {session.session_id}")
    print(f"[Student]: {session.student_name} ({session.student_id})")
    print(f"[Status]: Semester {session.current_semester} | CGPA: {session.cgpa:.2f} | Goal: {session.career_goal}")
    print(f"[Academic Standing]: {session.academic_standing}")

    print("\n--- [1] Agent 4: State Synthesizer Summary ---")
    print(session.student_state.synthesis_summary)

    print("\n--- [2] Agent 2: The Matrix Pathway Steps ---")
    print(f"Total Steps Required: {session.degree_pathway.total_steps_required}")
    for step in session.degree_pathway.path_sequence:
        print(f"  * {step.step_label}: {step.nodes_to_complete} ({step.step_total_credits_or_effort} credits)")

    print("\n--- [3] Agent 6: Sentinel Constraint & Conflict Report ---")
    print(f"Has Conflicts: {session.conflict_report.has_conflicts}")
    print(f"Risk Index: {session.conflict_report.graduation_risk_score * 100:.0f}%")
    print(f"Summary: {session.conflict_report.summary}")

    print("\n--- [4] Agent 5: Codex Graph-RAG Grounded Citations ---")
    for cite in session.graph_rag_advising.matched_policies:
        print(f"  * {cite.citation_code} - {cite.title}")

    print("\n--- [5] Agent 3: Vector Strategic Career Plan ---")
    print(session.career_vector.raw_markdown)

    print("\n--- [6] Multi-Agent Telemetry ---")
    for t in session.agent_telemetry:
        print(f"  * [{t['agent']}]: {t['action']} ({t['duration_ms']}ms) -> {t['status']}")

    print("\n--- [7] Interactive Chat Query Test ---")
    chat_res = nexus.process_chat_message(sample_id, "How can I get a waiver for Deep Learning prerequisite?")
    print(f"Question: 'How can I get a waiver for Deep Learning prerequisite?'")
    print(f"Answer: {chat_res['reply']}")
    print(f"Citations: {chat_res['citations']}")

    print("\n" + "=" * 80)
    print(" ALL 6 AGENTS EXECUTED SUCCESSFULLY WITH ZERO ERRORS")
    print("=" * 80)


if __name__ == "__main__":
    test_full_pipeline()
