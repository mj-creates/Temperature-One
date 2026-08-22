"""
University Curriculum Graph Builder for Agent Matrix.
Extracts courses, prerequisites, corequisites, antirequisites, and course substitutions from SQLite.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .matrix_graph import GraphNode, PrerequisiteGraph
except ImportError:
    from matrix_graph import GraphNode, PrerequisiteGraph

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "university.db"


def build_curriculum_graph_from_db(db_path: Optional[Union[str, Path]] = None) -> PrerequisiteGraph:
    """
    Constructs a PrerequisiteGraph by reading subjects and explicit prerequisite relations
    directly from the SQLite university database.
    """
    graph = PrerequisiteGraph()
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH

    if not target_db.exists():
        return graph

    try:
        conn = sqlite3.connect(str(target_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT SubjectID, SubjectName, Semester, Credits FROM Subjects ORDER BY Semester, SubjectID;")
        subjects_rows = cursor.fetchall()

        cursor.execute("SELECT SubjectID, PrereqSubjectID, PrereqType FROM Prerequisites;")
        prereq_rows = cursor.fetchall()

        prereq_map: Dict[str, List[str]] = {}
        coreq_map: Dict[str, List[str]] = {}
        antireq_map: Dict[str, List[str]] = {}

        for row in prereq_rows:
            sid = row["SubjectID"]
            prereq_id = row["PrereqSubjectID"]
            ptype = row["PrereqType"]

            if ptype == "HARD_PREREQ":
                prereq_map.setdefault(sid, []).append(prereq_id)
            elif ptype == "COREQ":
                coreq_map.setdefault(sid, []).append(prereq_id)
            elif ptype == "ANTIREQ":
                antireq_map.setdefault(sid, []).append(prereq_id)

        conn.close()

        for row in subjects_rows:
            sid = row["SubjectID"]
            node = GraphNode(
                node_id=sid,
                name=row["SubjectName"],
                credits=row["Credits"],
                semester=row["Semester"],
                prerequisites=prereq_map.get(sid, []),
                corequisites=coreq_map.get(sid, []),
                antirequisites=antireq_map.get(sid, []),
            )
            graph.add_node(node)

        return graph
    except Exception as e:
        print(f"[WARN] Error loading curriculum graph from DB: {e}")
        return graph


def build_custom_graph(nodes_payload: List[Dict[str, Any]]) -> PrerequisiteGraph:
    """
    Builds a PrerequisiteGraph from custom node dictionaries.
    """
    graph = PrerequisiteGraph()
    for item in nodes_payload:
        node = GraphNode(
            node_id=item.get("node_id") or item.get("id") or item.get("SubjectID"),
            name=item.get("name") or item.get("SubjectName", ""),
            credits=item.get("credits") or item.get("Credits", 3.0),
            semester=item.get("semester") or item.get("Semester"),
            prerequisites=item.get("prerequisites") or item.get("prereqs", []),
            corequisites=item.get("corequisites") or item.get("coreqs", []),
            antirequisites=item.get("antirequisites") or item.get("antireqs", []),
        )
        graph.add_node(node)
    return graph


def get_course_substitutions_from_db(subject_id: str, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieves valid course substitutions and elective alternatives from the database."""
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not target_db.exists():
        return []

    try:
        conn = sqlite3.connect(str(target_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                ce.SubjectID, ce.EquivalentSubjectID, ce.EquivalenceType,
                s.SubjectName as EquivalentName, s.Credits, s.Semester
            FROM Course_Equivalences ce
            JOIN Subjects s ON ce.EquivalentSubjectID = s.SubjectID
            WHERE ce.SubjectID = ?;
        """, (subject_id,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(r) for r in rows]
    except Exception:
        return []


def export_react_flow_graph(
    db_path: Optional[Path] = None,
    student_completed_nodes: Optional[List[str]] = None,
    student_enrolled_nodes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Exports curriculum nodes and edges structured specifically for React Flow rendering.
    Positions nodes in distinct columns by semester (Sem 1 to Sem 4).
    """
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH
    completed_set = set(student_completed_nodes or [])
    enrolled_set = set(student_enrolled_nodes or [])

    nodes = []
    edges = []

    if not target_db.exists():
        return {"nodes": [], "edges": []}

    try:
        conn = sqlite3.connect(str(target_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT SubjectID, SubjectName, Semester, Credits FROM Subjects ORDER BY Semester, SubjectID;")
        subject_rows = cursor.fetchall()

        cursor.execute("SELECT PrereqID, SubjectID, PrereqSubjectID, PrereqType FROM Prerequisites;")
        prereq_rows = cursor.fetchall()
        conn.close()

        semester_counters: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
        
        for row in subject_rows:
            sid = row["SubjectID"]
            sem = row["Semester"]
            name = row["SubjectName"]
            credits = row["Credits"]

            idx_in_sem = semester_counters[sem]
            semester_counters[sem] += 1

            if sid in completed_set:
                status = "COMPLETED"
            elif sid in enrolled_set:
                status = "ENROLLED"
            else:
                status = "AVAILABLE"

            is_bottleneck = sid in ("Sub_2_1", "Sub_3_1", "Sub_3_2", "Sub_3_3", "Sub_4_1")

            x_pos = (sem - 1) * 360 + 50
            y_pos = idx_in_sem * 120 + 60

            nodes.append({
                "id": sid,
                "type": "customCourseNode",
                "position": {"x": x_pos, "y": y_pos},
                "data": {
                    "subject_id": sid,
                    "label": name,
                    "credits": credits,
                    "semester": sem,
                    "status": status,
                    "is_bottleneck": is_bottleneck
                }
            })

        for r in prereq_rows:
            target_id = r["SubjectID"]
            source_id = r["PrereqSubjectID"]
            ptype = r["PrereqType"]
            edge_id = f"edge_{source_id}_{target_id}_{ptype}"

            is_active_path = (source_id in completed_set or source_id in enrolled_set) and (target_id in enrolled_set)

            edge_data = {
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "type": "smoothstep",
                "animated": is_active_path or ptype == "COREQ",
                "style": {
                    "stroke": "#10b981" if is_active_path else ("#3b82f6" if ptype == "HARD_PREREQ" else ("#f59e0b" if ptype == "COREQ" else "#ef4444")),
                    "strokeWidth": 2.5 if is_active_path else 1.5,
                    "strokeDasharray": "5,5" if ptype == "COREQ" else None
                },
                "data": {
                    "type": ptype
                }
            }
            edges.append(edge_data)

        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        print(f"[WARN] Error exporting React Flow graph: {e}")
        return {"nodes": [], "edges": []}
