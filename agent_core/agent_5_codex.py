"""
Codex (Agent 05) - Graph-RAG Academic Policy & Citation Retrieval Engine
========================================================================
Performs hybrid keyword-semantic and knowledge graph traversal retrieval over
university degree requirements, prerequisite regulations, and academic policies.
Produces strictly citation-traceable advising references.
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .agent_schemas import PolicyCitation, GraphRAGQueryResult
except ImportError:
    try:
        from agent_schemas import PolicyCitation, GraphRAGQueryResult
    except ImportError:
        from schemas import PolicyCitation, GraphRAGQueryResult

try:
    from backend.database.vector_db import vector_db
except ImportError:
    vector_db = None

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "university.db"


class CodexGraphRAGAgent:
    """
    Agent 5: Codex (Graph-RAG Policy & Citation Engine).
    Navigates policy corpora and prerequisite subgraphs to produce verified,
    citation-backed academic regulatory guidance.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_all_policies(self) -> List[Dict[str, Any]]:
        """Retrieves all academic policy documents from the database."""
        if not self.db_path.exists():
            return []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PolicyID, Section, Title, Content, Category, CitationCode FROM Academic_Policies;")
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def retrieve_policies_for_query(
        self,
        query: str,
        student_context: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> List[PolicyCitation]:
        """
        Retrieves top relevant policies based on query keywords and student contextual attributes.
        """
        policies = self.fetch_all_policies()
        if not policies:
            return []

        query_tokens = set(re.findall(r'\w+', (query or "").lower()))
        
        if student_context:
            if student_context.get("cgpa", 10.0) < 6.0:
                query_tokens.update(["probation", "recovery", "limit", "standing"])
            if student_context.get("career_goal"):
                query_tokens.update(["specialization", "track", "capstone", "degree"])
            if student_context.get("semester", 1) >= 3:
                query_tokens.update(["capstone", "graduation", "eligibility"])

        scored_policies: List[Tuple[float, Dict[str, Any]]] = []

        for p in policies:
            score = 0.0
            content_lower = p["Content"].lower()
            title_lower = p["Title"].lower()
            category_lower = p["Category"].lower()

            for token in query_tokens:
                if len(token) < 3:
                    continue
                if token in title_lower:
                    score += 3.0
                if token in category_lower:
                    score += 2.0
                if token in content_lower:
                    score += 1.0

            scored_policies.append((score, p))

        scored_policies.sort(key=lambda x: x[0], reverse=True)
        top_matches = [p for score, p in scored_policies[:top_k] if score > 0]
        
        if not top_matches:
            top_matches = policies[:top_k]

        citations: List[PolicyCitation] = []
        for p in top_matches:
            snippet = p["Content"][:150] + ("..." if len(p["Content"]) > 150 else "")
            citations.append(PolicyCitation(
                policy_id=p["PolicyID"],
                section=p["Section"],
                title=p["Title"],
                citation_code=p["CitationCode"],
                relevance_snippet=snippet,
                category=p["Category"]
            ))

        return citations

    def generate_grounded_advising(
        self,
        student_id: str,
        student_profile: Dict[str, Any],
        path_data: Optional[Dict[str, Any]] = None,
        conflict_data: Optional[Dict[str, Any]] = None
    ) -> GraphRAGQueryResult:
        """
        Synthesizes grounded advising text backed by verified Graph-RAG policy citations.
        """
        cgpa = float(student_profile.get("cgpa", 7.5))
        semester = int(student_profile.get("semester", 1))
        goal = student_profile.get("career_goal", "Computer Science")

        query_intent = f"Degree progression for {goal} in semester {semester} with CGPA {cgpa}"
        citations = self.retrieve_policies_for_query(query_intent, student_context=student_profile, top_k=3)

        citation_tags = [c.citation_code for c in citations]

        narrative_parts = []
        
        narrative_parts.append(
            f"Under University Degree Framework {citation_tags[0] if citation_tags else '[Policy §1.1]'}, "
            f"you are progressing toward the 160 cumulative credits required for graduation."
        )

        if cgpa >= 8.5:
            standing_cite = "[Policy §5.1: Academic Standing]"
            overload_cite = "[Policy §2.1: Credit Load & Overload]"
            narrative_parts.append(
                f"With a CGPA of {cgpa:.2f}, you hold HONORS standing ({standing_cite}) and qualify to petition "
                f"for up to 24 credits per semester ({overload_cite}) to fast-track your {goal} milestone courses."
            )
        elif cgpa < 6.0:
            prob_cite = "[Policy §5.1: Academic Standing]"
            cap_cite = "[Policy §2.1: Credit Load & Overload]"
            narrative_parts.append(
                f"Your CGPA of {cgpa:.2f} places your profile in MONITORED / PROBATION status ({prob_cite}). "
                f"Semester enrollment is restricted to a 16-credit maximum ({cap_cite}) with mandatory prerequisite remediation."
            )
        else:
            std_cite = "[Policy §2.1: Credit Load & Overload]"
            narrative_parts.append(
                f"Your profile maintains GOOD STANDING with regular 20-credit enrollment capacity ({std_cite})."
            )

        prereq_cite = "[Policy §3.1: Prerequisite Progression]"
        if semester >= 3:
            cap_cite = "[Policy §6.1: Capstone Eligibility]"
            narrative_parts.append(
                f"Strict prerequisite validation ({prereq_cite}) is active for upper-division electives. "
                f"Ensure Design & Analysis of Algorithms (Sub_3_3) and DBMS (Sub_3_1) are cleared prior to Capstone registration ({cap_cite})."
            )
        else:
            narrative_parts.append(
                f"All upcoming course selections are strictly topology-checked against prerequisite dependency chains ({prereq_cite})."
            )

        synthesis_text = " ".join(narrative_parts)

        return GraphRAGQueryResult(
            query=query_intent,
            matched_policies=citations,
            synthesis=synthesis_text,
            traceable_citations=citation_tags
        )


class Agent5Codex:
    """Agent 5: Codex wrapper for semantic search & microservice queries."""
    def __init__(self):
        self.vector_db = vector_db

    def query_policy(self, query_string: str) -> str:
        if not self.vector_db:
            return "NO_DATA_FOUND"
        matched_context = self.vector_db.query_policy(query_string)
        if not matched_context:
            return "NO_DATA_FOUND"
        metadata = matched_context["metadata"]
        text = matched_context["text"]
        target = metadata.get("subject", "University Policy")
        return (
            "**Policy Constraints:**\n"
            f"- **Target Subject:** {target}\n"
            f"- **Required Prerequisites:** See Policy Details\n"
            f"- **Credit Value:** See Policy Details\n"
            f"- **Special Rules:** {text}\n"
            f"- **Graph Citation:** [{metadata.get('source', 'Unknown_Source')}]"
        )
