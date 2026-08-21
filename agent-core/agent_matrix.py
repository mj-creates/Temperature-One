"""
Agent 2: "The Matrix" (Graph Navigator & Pathfinder)
Autonomous routing and pathfinding engine within the Anti Gravity autonomous pipeline.
Computes conflict-free, optimized chronological sequences across prerequisite webs.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

try:
    from .schemas import (
        MatrixPathResponse,
        MatrixErrorResponse,
        STATUS_VALID,
        STATUS_PATH_UNREACHABLE,
        STATUS_GRAPH_ERROR,
        STATUS_ALREADY_ACHIEVED,
        ERROR_MISSING_CRITICAL_NODE,
        ERROR_CYCLIC_DEPENDENCY,
    )
    from .matrix_graph import GraphNode, PrerequisiteGraph
    from .matrix_curriculum import (
        build_curriculum_graph_from_db,
        build_custom_graph,
        DEFAULT_DB_PATH,
    )
    from .matrix_pathfinder import compute_matrix_path, format_matrix_error
    from .prompts import MATRIX_SYSTEM_PROMPT, get_matrix_prompt
except ImportError:
    from schemas import (
        MatrixPathResponse,
        MatrixErrorResponse,
        STATUS_VALID,
        STATUS_PATH_UNREACHABLE,
        STATUS_GRAPH_ERROR,
        STATUS_ALREADY_ACHIEVED,
        ERROR_MISSING_CRITICAL_NODE,
        ERROR_CYCLIC_DEPENDENCY,
    )
    from matrix_graph import GraphNode, PrerequisiteGraph
    from matrix_curriculum import (
        build_curriculum_graph_from_db,
        build_custom_graph,
        DEFAULT_DB_PATH,
    )
    from matrix_pathfinder import compute_matrix_path, format_matrix_error
    from prompts import MATRIX_SYSTEM_PROMPT, get_matrix_prompt


class MatrixAgent:
    """
    Agent 2: The Matrix (Graph Navigator & Pathfinder).

    Navigates course and task prerequisite graphs, calculates critical paths,
    enforces temporal constraints, and outputs optimized sequence JSON.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.system_prompt = MATRIX_SYSTEM_PROMPT
        self._cached_graph: Optional[PrerequisiteGraph] = None

    def get_graph(self) -> PrerequisiteGraph:
        """Loads and caches the curriculum prerequisite graph."""
        if self._cached_graph is None:
            self._cached_graph = build_curriculum_graph_from_db(self.db_path)
        return self._cached_graph

    def compute_path(
        self,
        student_id: str,
        target_node: str,
        completed_nodes: Optional[Union[List[str], Set[str]]] = None,
        custom_graph_nodes: Optional[List[Dict[str, Any]]] = None,
        max_credits_per_step: float = 20.0,
        step_label_prefix: str = "Semester",
    ) -> str:
        """
        Computes the optimal path to target_node given completed nodes.

        Returns:
            Raw valid JSON string adhering strictly to Matrix output schema or error protocol.
        """
        if not student_id or not str(student_id).strip():
            student_id = "UNKNOWN_STUDENT"
        if not target_node or not str(target_node).strip():
            return format_matrix_error(STATUS_PATH_UNREACHABLE, ERROR_MISSING_CRITICAL_NODE)

        # Build or use graph
        if custom_graph_nodes:
            graph = build_custom_graph(custom_graph_nodes)
        else:
            graph = self.get_graph()

        return compute_matrix_path(
            student_id=student_id,
            target_node=target_node,
            graph=graph,
            completed_nodes=completed_nodes,
            max_credits_per_step=max_credits_per_step,
            step_label_prefix=step_label_prefix,
        )

    def compute_path_from_student_state(
        self,
        student_state: Union[str, Dict[str, Any]],
        target_node: str,
        custom_graph_nodes: Optional[List[Dict[str, Any]]] = None,
        max_credits_per_step: float = 20.0,
    ) -> str:
        """
        Accepts the output from Agent 4 (Student State JSON/dict) and computes the path to target_node.
        """
        if isinstance(student_state, str):
            try:
                state_dict = json.loads(student_state)
            except Exception:
                return format_matrix_error(STATUS_GRAPH_ERROR, "INVALID_STATE_PAYLOAD")
        elif isinstance(student_state, dict):
            state_dict = student_state
        else:
            return format_matrix_error(STATUS_GRAPH_ERROR, "INVALID_STATE_PAYLOAD")

        student_id = state_dict.get("student_id", "STUDENT")

        # Extract completed courses from state if available
        completed_nodes = state_dict.get("completed_nodes", [])
        if not completed_nodes and "enrolled_subjects" in state_dict:
            completed_nodes = [
                s.get("SubjectID") or s.get("subject_id")
                for s in state_dict["enrolled_subjects"]
                if isinstance(s, dict)
            ]

        # If student ID is in DB, extract their registered subjects as completed baseline
        if not completed_nodes and self.db_path.exists():
            db_completed = self._fetch_student_completed_from_db(student_id)
            if db_completed:
                completed_nodes = db_completed

        return self.compute_path(
            student_id=student_id,
            target_node=target_node,
            completed_nodes=completed_nodes,
            custom_graph_nodes=custom_graph_nodes,
            max_credits_per_step=max_credits_per_step,
        )

    def _fetch_student_completed_from_db(self, student_id: str) -> List[str]:
        """Fetches completed/enrolled subject IDs for a student from SQLite DB."""
        if not self.db_path.exists():
            return []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT SubjectID FROM Student_Subjects WHERE RegNo = ?;", (student_id,))
            rows = cursor.fetchall()
            conn.close()
            return [row[0] for row in rows if row and row[0]]
        except Exception:
            return []

    def compute_path_from_db(
        self,
        student_id: str,
        target_node: str,
        max_credits_per_step: float = 20.0
    ) -> str:
        """
        Fetches student state directly from university SQLite database and computes the path.
        """
        completed_nodes = self._fetch_student_completed_from_db(student_id)
        return self.compute_path(
            student_id=student_id,
            target_node=target_node,
            completed_nodes=completed_nodes,
            max_credits_per_step=max_credits_per_step,
        )

    def process_plan(
        self,
        student_id: str,
        target_node: str,
        state_payload: Optional[Union[str, Dict[str, Any]]] = None,
        next_agent: Optional[Any] = None
    ) -> str:
        """
        Pipeline execution method. Connects with upstream Agent 1 (Nexus) / Agent 4 (State)
        and hands off results to downstream Agent 3 (Vector) if present.
        """
        if state_payload:
            result_json = self.compute_path_from_student_state(state_payload, target_node)
        else:
            result_json = self.compute_path_from_db(student_id, target_node)

        if next_agent and hasattr(next_agent, "process_schedule"):
            return next_agent.process_schedule(student_id, target_node, result_json)

        return result_json


# Functional wrapper
def run_matrix(
    student_id: str,
    target_node: str,
    completed_nodes: Optional[List[str]] = None,
    db_path: Optional[Path] = None
) -> str:
    """Convenience functional wrapper for Agent - The Matrix."""
    agent = MatrixAgent(db_path=db_path)
    return agent.compute_path(student_id=student_id, target_node=target_node, completed_nodes=completed_nodes)
