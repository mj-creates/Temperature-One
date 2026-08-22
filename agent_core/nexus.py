"""
Nexus (Agent 01) - Front Desk & Central Supervisor Agent
========================================================
The central orchestration hub for the intelligent multi-agent Academic Advising System.
Coordinates Nexus -> State -> Matrix -> Vector -> Codex Graph-RAG -> Sentinel.
"""

import json
import time
import uuid
from pathlib import Path
from typing import Optional, Any, Dict, List

try:
    from .schemas import (
        AdvisingSessionResponse,
        StudentState,
        MatrixPathResponse,
        ConflictDiagnosticReport,
        MomentumPlan,
        GraphRAGQueryResult,
        FacultyPetitionRecord,
    )
    from .agent_4_background_check import Agent4BackgroundCheck
    from .agent_matrix import MatrixAgent
    from .agent_3_vector import Agent3Vector
    from .agent_codex_rag import CodexGraphRAGAgent
    from .agent_sentinel_verifier import SentinelVerifierAgent
except ImportError:
    from schemas import (
        AdvisingSessionResponse,
        StudentState,
        MatrixPathResponse,
        ConflictDiagnosticReport,
        MomentumPlan,
        GraphRAGQueryResult,
        FacultyPetitionRecord,
    )
    from agent_4_background_check import Agent4BackgroundCheck
    from agent_matrix import MatrixAgent
    from agent_3_vector import Agent3Vector
    from agent_codex_rag import CodexGraphRAGAgent
    from agent_sentinel_verifier import SentinelVerifierAgent

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "university.db"


class NexusAgent:
    """
    Agent 1 (The Front Desk): Nexus.
    Supervisor Agent responsible for student intake, intent routing, and full multi-agent pipeline orchestration.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.agent_state = Agent4BackgroundCheck(db_path=self.db_path)
        self.agent_matrix = MatrixAgent(db_path=self.db_path)
        self.agent_vector = Agent3Vector()
        self.agent_codex = CodexGraphRAGAgent(db_path=self.db_path)
        self.agent_sentinel = SentinelVerifierAgent(db_path=self.db_path)

    def run_full_advising_pipeline(
        self,
        student_id: str,
        custom_goal: Optional[str] = None
    ) -> AdvisingSessionResponse:
        """
        Orchestrates the entire decentralized multi-agent advising session:
        1. Agent 4: State Synthesizer (DBMS inspection & sanitization)
        2. Agent 2: The Matrix (Topological degree progression pathway)
        3. Agent 6: Sentinel (Formal constraint & conflict verification)
        4. Agent 5: Codex (Graph-RAG policy grounding & citation retrieval)
        5. Agent 3: Vector (Strategic career momentum plan)
        """
        session_id = f"SES_{uuid.uuid4().hex[:8].upper()}"
        telemetry = []

        # -------------------------------------------------------------------
        # Step 1: Agent 4 (The Background Check / State Synthesizer)
        # -------------------------------------------------------------------
        t0 = time.time()
        raw_record, err = self.agent_state.fetch_raw_student_from_db(student_id)
        if err or not raw_record:
            raise ValueError(f"Student ID '{student_id}' could not be located in database.")

        if custom_goal:
            raw_record["career_goal"] = custom_goal

        state_json = self.agent_state.inspect_raw_payload(raw_record)
        student_state = StudentState.model_validate_json(state_json)
        
        telemetry.append({
            "agent": "Agent 4 (State Synthesizer)",
            "action": "Sanitized Student Profile Extraction",
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "status": "SUCCESS"
        })

        # Extract student profile attributes
        student_name = raw_record.get("student_name", "Student")
        current_semester = raw_record.get("semester", 1)
        cgpa = float(raw_record.get("current_gpa", 7.5))
        career_goal = raw_record.get("career_goal", "Computer Science")
        academic_standing = student_state.academic_state.academic_standing or "GOOD_STANDING"

        enrolled_subjects = raw_record.get("enrolled_subjects", [])
        enrolled_ids = [s.get("SubjectID") for s in enrolled_subjects if s.get("SubjectID")]
        
        # Completed nodes: assume baseline from prior semesters or enrolled
        completed_ids = enrolled_ids[:]

        # -------------------------------------------------------------------
        # Step 2: Agent 2 (The Matrix - Graph Navigator & Pathway Planner)
        # -------------------------------------------------------------------
        t0 = time.time()
        pathway = self.agent_matrix.generate_degree_progression_pathway(
            student_id=student_id,
            current_semester=current_semester,
            completed_nodes=completed_ids,
            career_goal=career_goal,
            max_credits_per_semester=24.0 if cgpa >= 8.0 else (16.0 if cgpa < 6.0 else 20.0)
        )
        telemetry.append({
            "agent": "Agent 2 (The Matrix)",
            "action": "Topological Degree Pathway Calculation",
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "status": "SUCCESS",
            "steps_count": pathway.total_steps_required
        })

        # -------------------------------------------------------------------
        # Step 3: Agent 6 (Sentinel - Formal Constraint & Conflict Verifier)
        # -------------------------------------------------------------------
        t0 = time.time()
        conflict_report = self.agent_sentinel.evaluate_student_conflicts_and_risks(
            student_id=student_id,
            student_profile={"cgpa": cgpa, "semester": current_semester, "career_goal": career_goal},
            enrolled_subject_ids=enrolled_ids,
            completed_subject_ids=completed_ids
        )
        petitions = self.agent_sentinel.fetch_petitions_for_student(student_id)
        telemetry.append({
            "agent": "Agent 6 (Sentinel Verifier)",
            "action": "Formal Constraint Audit & Risk Scoring",
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "status": "SUCCESS",
            "conflicts_detected": len(conflict_report.conflicts)
        })

        # -------------------------------------------------------------------
        # Step 4: Agent 5 (Codex - Graph-RAG Policy & Citation Engine)
        # -------------------------------------------------------------------
        t0 = time.time()
        graph_rag = self.agent_codex.generate_grounded_advising(
            student_id=student_id,
            student_profile={"cgpa": cgpa, "semester": current_semester, "career_goal": career_goal},
            path_data=pathway.model_dump(),
            conflict_data=conflict_report.model_dump()
        )
        telemetry.append({
            "agent": "Agent 5 (Codex Graph-RAG)",
            "action": "Policy Knowledge Graph Clause Retrieval",
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "status": "SUCCESS",
            "citations_matched": len(graph_rag.matched_policies)
        })

        # -------------------------------------------------------------------
        # Step 5: Agent 3 (Vector - Strategic Career Trajectory Engine)
        # -------------------------------------------------------------------
        t0 = time.time()
        vector_plan = self.agent_vector.generate_momentum_plan(
            student_goal=career_goal,
            matrix_schedule=pathway.model_dump(),
            cgpa=cgpa
        )
        telemetry.append({
            "agent": "Agent 3 (Vector)",
            "action": "Career Velocity & Momentum Planning",
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "status": "SUCCESS"
        })

        # -------------------------------------------------------------------
        # Step 6: Agent 1 (Nexus Synthesis Narrative)
        # -------------------------------------------------------------------
        all_citations = graph_rag.traceable_citations
        if conflict_report.conflicts:
            for c in conflict_report.conflicts:
                if c.policy_citation and c.policy_citation not in all_citations:
                    all_citations.append(c.policy_citation)

        advising_narrative = (
            f"### Academic Advising Briefing for {student_name} ({student_id})\n\n"
            f"**Current Status:** Semester {current_semester} | CGPA: {cgpa:.2f} / 10.00 ({academic_standing})\n"
            f"**Target Specialization:** {career_goal}\n\n"
            f"#### 🏛️ Regulatory & Policy Grounding\n"
            f"{graph_rag.synthesis}\n\n"
            f"#### 🗺️ Degree Progression & Topological Roadmap\n"
            f"{pathway.matrix_analysis}\n"
            f"*Total Future Steps Required:* {pathway.total_steps_required} term(s) across critical gateway courses ({', '.join(pathway.bottlenecks)}).\n\n"
            f"#### ⚠️ Constraint Diagnostics & Risk Assessment\n"
            f"{conflict_report.summary}\n\n"
            f"#### 🚀 Career Momentum Plan (Vector Engine)\n"
            f"{vector_plan.raw_markdown}\n"
        )

        return AdvisingSessionResponse(
            session_id=session_id,
            student_id=student_id,
            student_name=student_name,
            current_semester=current_semester,
            cgpa=cgpa,
            career_goal=career_goal,
            academic_standing=academic_standing,
            student_state=student_state,
            degree_pathway=pathway,
            conflict_report=conflict_report,
            career_vector=vector_plan,
            graph_rag_advising=graph_rag,
            faculty_petitions=petitions,
            advising_narrative=advising_narrative,
            citations=all_citations,
            agent_telemetry=telemetry
        )

    def process_chat_message(
        self,
        student_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Handles interactive conversational advising inquiries with citation-traceable answers.
        """
        raw_record, err = self.agent_state.fetch_raw_student_from_db(student_id)
        if err or not raw_record:
            return {
                "reply": f"Could not find records for student ID '{student_id}'. Please verify your Registration Number.",
                "citations": []
            }

        cgpa = float(raw_record.get("current_gpa", 7.5))
        sem = int(raw_record.get("semester", 1))
        goal = raw_record.get("career_goal", "Software Engineering")
        name = raw_record.get("student_name", "Student")

        query_citations = self.agent_codex.retrieve_policies_for_query(
            message,
            student_context={"cgpa": cgpa, "semester": sem, "career_goal": goal},
            top_k=2
        )

        msg_lower = message.lower()
        citations = [c.citation_code for c in query_citations]

        if "waiver" in msg_lower or "petition" in msg_lower:
            reply = (
                f"Hello {name}, according to {citations[0] if citations else '[Policy §3.2: Prerequisite Waiver]'}, "
                f"prerequisite waivers require a formal Faculty Petition with documented external credentials (e.g. Coursera/certifications) "
                f"or department chair approval. You can submit a petition directly through the Faculty Portal tab."
            )
        elif "credit" in msg_lower or "overload" in msg_lower or "max" in msg_lower:
            reply = (
                f"Under {citations[0] if citations else '[Policy §2.1: Credit Load & Overload]'}, the standard semester load is 20 credits. "
                f"With your current CGPA of {cgpa:.2f}, you {'qualify for up to 24 credits per semester' if cgpa >= 8.0 else 'are capped at standard 20 credits (8.0+ CGPA needed for 24-credit overload)'}."
            )
        elif "career" in msg_lower or "job" in msg_lower or "internship" in msg_lower or "project" in msg_lower:
            vplan = self.agent_vector.generate_momentum_plan(goal)
            reply = (
                f"For your target track as **{goal}**, our Vector Engine recommends:\n"
                f"- **Project:** {vplan.actionable_project}\n"
                f"- **Internship Focus:** {vplan.internship_target}\n"
                f"- **Target Certification:** {', '.join(vplan.target_certifications)}"
            )
        elif "capstone" in msg_lower or "research" in msg_lower:
            reply = (
                f"Per [Policy §6.1: Capstone Eligibility], Applied Capstone Research (Sub_4_15) requires 4th semester standing, "
                f"minimum 60 earned credits, and passing grades in Design & Analysis of Algorithms (Sub_3_3) and DBMS (Sub_3_1)."
            )
        else:
            reply = (
                f"Nexus Advisor: Based on your academic record in Semester {sem} ({goal} track, CGPA {cgpa:.2f}), "
                f"your course selections are topologically aligned with degree requirements ({citations[0] if citations else '[Policy §1.1]'}). "
                f"You can explore the interactive Knowledge Graph or Conflict Center for detailed prerequisites."
            )

        return {
            "reply": reply,
            "citations": citations
        }

    def receive_student(self, reg_number: str, name: str, goal: str = "") -> Dict[str, Any]:
        """
        Intake handler for a student advising session.
        """
        greeting = f"Hello {name}! Welcome to your Academic Advising session. I'm Nexus, your front desk advisor."
        return {
            "greeting": greeting,
            "reg_number": reg_number,
            "name": name,
            "goal": goal or "Computer Science",
            "status": "READY_FOR_ADVISING"
        }



# Functional wrapper
def run_nexus(student_id: str, goal: Optional[str] = None, db_path: Optional[Path] = None) -> AdvisingSessionResponse:
    nexus = NexusAgent(db_path=db_path)
    return nexus.run_full_advising_pipeline(student_id, custom_goal=goal)
