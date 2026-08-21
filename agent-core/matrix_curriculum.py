"""
University Curriculum Graph Builder for Agent Matrix.
Extracts courses from SQLite database and establishes standard academic prerequisite chains.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from .matrix_graph import GraphNode, PrerequisiteGraph
except ImportError:
    from matrix_graph import GraphNode, PrerequisiteGraph

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "university.db"

# Canonical academic prerequisite chains mapped across CS catalog semesters
CANONICAL_PREREQUISITES: Dict[str, List[str]] = {
    # Semester 2 Prerequisites
    "Sub_2_1": ["Sub_1_1"],           # DSA requires Intro to Programming
    "Sub_2_2": ["Sub_1_1"],           # OOP Java requires Intro to Programming
    "Sub_2_3": ["Sub_1_2"],           # Linear Algebra requires Calculus
    "Sub_2_4": ["Sub_1_7"],           # Comp Arch requires Digital Logic
    "Sub_2_5": ["Sub_1_2"],           # Prob & Stats requires Calculus
    "Sub_2_7": ["Sub_1_1"],           # Software Eng requires Programming
    "Sub_2_9": ["Sub_1_1"],           # Relational DB requires Programming
    "Sub_2_10": ["Sub_1_10"],         # Automata requires Discrete Math
    "Sub_2_13": ["Sub_1_12"],         # Linux Scripting requires Hardware Lab

    # Semester 3 Prerequisites
    "Sub_3_1": ["Sub_2_9"],           # DBMS requires Relational DB Concepts
    "Sub_3_2": ["Sub_2_4", "Sub_2_13"],# Operating Systems requires Comp Arch & Linux
    "Sub_3_3": ["Sub_2_1"],           # Algorithms requires DSA
    "Sub_3_4": ["Sub_3_2"],           # Networks requires OS
    "Sub_3_5": ["Sub_2_3", "Sub_2_5"],# AI requires Linear Algebra & Prob/Stats
    "Sub_3_6": ["Sub_2_6"],           # Full Stack requires Web Dev Fundamentals
    "Sub_3_7": ["Sub_2_2"],           # Mobile App requires Java OOP
    "Sub_3_8": ["Sub_1_10"],          # Cryptography requires Discrete Math
    "Sub_3_9": ["Sub_2_4"],           # Cloud Computing requires Comp Arch
    "Sub_3_10": ["Sub_2_10"],         # Compiler Design requires Automata
    "Sub_3_11": ["Sub_2_9"],          # Data Warehousing requires Relational DB
    "Sub_3_12": ["Sub_2_1"],          # Distributed Systems requires DSA
    "Sub_3_13": ["Sub_2_13"],         # Cyber Forensics requires Linux
    "Sub_3_14": ["Sub_1_13"],         # NLP Basics requires Python Prototyping
    "Sub_3_15": ["Sub_2_7"],          # Agile & DevOps requires Software Eng

    # Semester 4 Prerequisites
    "Sub_4_1": ["Sub_3_3", "Sub_3_5"],# ML Systems requires Algorithms & AI
    "Sub_4_2": ["Sub_4_1"],           # Deep Learning requires ML Systems
    "Sub_4_3": ["Sub_3_1", "Sub_2_5"],# Big Data requires DBMS & Stats
    "Sub_4_4": ["Sub_3_15", "Sub_3_4"],# DevOps & CI/CD requires Agile & Networks
    "Sub_4_5": ["Sub_3_8"],           # Information Security requires Cryptography
    "Sub_4_6": ["Sub_3_4"],           # IoT requires Networks
    "Sub_4_7": ["Sub_3_5", "Sub_2_3"],# Computer Vision requires AI & Linear Algebra
    "Sub_4_8": ["Sub_3_8", "Sub_3_12"],# Blockchain requires Cryptography & Distributed Systems
    "Sub_4_9": ["Sub_3_9", "Sub_3_6"],# Cloud Microservices requires Cloud & Full-Stack
    "Sub_4_10": ["Sub_3_2"],          # Parallel Computing requires OS
    "Sub_4_11": ["Sub_4_1"],          # Reinforcement Learning requires ML Systems
    "Sub_4_12": ["Sub_2_7"],          # QA & Testing requires Software Eng
    "Sub_4_13": ["Sub_2_3"],          # Quantum Computing requires Linear Algebra
    "Sub_4_14": ["Sub_3_11"],         # Data Visualization requires Data Warehousing
    "Sub_4_15": ["Sub_3_3", "Sub_3_1"],# Capstone Project requires Algorithms & DBMS
}

# Canonical Co-requisite pairs (courses designed to be taken together or prior)
CANONICAL_COREQUISITES: Dict[str, List[str]] = {
    "Sub_1_12": ["Sub_1_7"],   # Hardware Lab + Digital Logic
    "Sub_3_6": ["Sub_3_1"],    # Full Stack Web + DBMS
}

# Canonical Anti-requisite pairs (mutually exclusive courses)
CANONICAL_ANTIREQUISITES: Dict[str, List[str]] = {
    # Example: Specialization alternatives
    "Sub_4_13": ["Sub_4_6"],   # Quantum Computing vs IoT Elective Track
}


def build_curriculum_graph_from_db(db_path: Optional[Union[str, Path]] = None) -> PrerequisiteGraph:
    """
    Constructs a PrerequisiteGraph by reading subjects from the university SQLite database
    and augmenting them with canonical curriculum prerequisites, co-requisites, and anti-requisites.
    """
    graph = PrerequisiteGraph()
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH

    if target_db.exists():
        try:
            conn = sqlite3.connect(str(target_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT SubjectID, SubjectName, Semester, Credits FROM Subjects;")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                sid = row["SubjectID"]
                node = GraphNode(
                    node_id=sid,
                    name=row["SubjectName"],
                    credits=row["Credits"],
                    semester=row["Semester"],
                    prerequisites=CANONICAL_PREREQUISITES.get(sid, []),
                    corequisites=CANONICAL_COREQUISITES.get(sid, []),
                    antirequisites=CANONICAL_ANTIREQUISITES.get(sid, []),
                )
                graph.add_node(node)
            return graph
        except Exception:
            pass

    # Fallback default generation if DB is unavailable
    for sem in range(1, 5):
        for i in range(1, 16):
            sid = f"Sub_{sem}_{i}"
            credits = 4 if i in (1, 2, 4, 7, 10) else 3
            node = GraphNode(
                node_id=sid,
                name=f"Course {sid}",
                credits=credits,
                semester=sem,
                prerequisites=CANONICAL_PREREQUISITES.get(sid, []),
                corequisites=CANONICAL_COREQUISITES.get(sid, []),
                antirequisites=CANONICAL_ANTIREQUISITES.get(sid, []),
            )
            graph.add_node(node)

    return graph


def build_custom_graph(nodes_payload: List[Dict[str, Any]]) -> PrerequisiteGraph:
    """
    Builds a PrerequisiteGraph from custom user-supplied node dictionaries.
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
