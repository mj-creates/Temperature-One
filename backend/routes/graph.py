"""
Curriculum Knowledge Graph Route
================================
Serves structured graph nodes and edges to the React Vite frontend
for interactive visualization with React Flow, Cytoscape, or D3.js.
"""

from typing import List, Dict, Any, Set
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import sqlite3

from backend.database.database import get_db_connection
from backend.database.crud import get_all_subjects
from backend.domain_schemas import (
    GraphNode,
    GraphEdge,
    CurriculumGraphResponse,
)

router = APIRouter(prefix="/api/graph", tags=["Curriculum Knowledge Graph"])


def get_db():
    """Dependency to provide SQLite database connection with auto-close."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Curriculum Dependency Graph Rules (Prerequisites, Co-requisites, Anti-requisites)
# ---------------------------------------------------------------------------
CURRICULUM_DEPENDENCIES: Dict[str, Dict[str, Any]] = {
    # Semester 1
    "Sub_1_1": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_2": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_3": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_4": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_5": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_6": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_7": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_8": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_9": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_10": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_11": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_12": {"prereqs": [], "coreqs": ["Sub_1_7"], "antireqs": []},
    "Sub_1_13": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_14": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_1_15": {"prereqs": [], "coreqs": [], "antireqs": []},

    # Semester 2
    "Sub_2_1": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []},
    "Sub_2_2": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []},
    "Sub_2_3": {"prereqs": ["Sub_1_2"], "coreqs": [], "antireqs": []},
    "Sub_2_4": {"prereqs": ["Sub_1_7"], "coreqs": [], "antireqs": []},
    "Sub_2_5": {"prereqs": ["Sub_1_2"], "coreqs": [], "antireqs": []},
    "Sub_2_6": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_7": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []},
    "Sub_2_8": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_9": {"prereqs": ["Sub_1_1"], "coreqs": [], "antireqs": []},
    "Sub_2_10": {"prereqs": ["Sub_1_10"], "coreqs": [], "antireqs": []},
    "Sub_2_11": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_12": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_13": {"prereqs": ["Sub_1_12"], "coreqs": [], "antireqs": []},
    "Sub_2_14": {"prereqs": [], "coreqs": [], "antireqs": []},
    "Sub_2_15": {"prereqs": [], "coreqs": [], "antireqs": []},

    # Semester 3
    "Sub_3_1": {"prereqs": ["Sub_2_9"], "coreqs": [], "antireqs": []},
    "Sub_3_2": {"prereqs": ["Sub_2_4", "Sub_2_13"], "coreqs": [], "antireqs": []},
    "Sub_3_3": {"prereqs": ["Sub_2_1"], "coreqs": [], "antireqs": []},
    "Sub_3_4": {"prereqs": ["Sub_3_2"], "coreqs": [], "antireqs": []},
    "Sub_3_5": {"prereqs": ["Sub_2_3", "Sub_2_5"], "coreqs": [], "antireqs": []},
    "Sub_3_6": {"prereqs": ["Sub_2_6"], "coreqs": ["Sub_3_1"], "antireqs": []},
    "Sub_3_7": {"prereqs": ["Sub_2_2"], "coreqs": [], "antireqs": []},
    "Sub_3_8": {"prereqs": ["Sub_1_10"], "coreqs": [], "antireqs": []},
    "Sub_3_9": {"prereqs": ["Sub_2_4"], "coreqs": [], "antireqs": []},
    "Sub_3_10": {"prereqs": ["Sub_2_10"], "coreqs": [], "antireqs": []},
    "Sub_3_11": {"prereqs": ["Sub_2_9"], "coreqs": [], "antireqs": []},
    "Sub_3_12": {"prereqs": ["Sub_2_1"], "coreqs": [], "antireqs": []},
    "Sub_3_13": {"prereqs": ["Sub_2_13"], "coreqs": [], "antireqs": []},
    "Sub_3_14": {"prereqs": ["Sub_1_13"], "coreqs": [], "antireqs": []},
    "Sub_3_15": {"prereqs": ["Sub_2_7"], "coreqs": [], "antireqs": []},

    # Semester 4
    "Sub_4_1": {"prereqs": ["Sub_3_3", "Sub_3_5"], "coreqs": [], "antireqs": []},
    "Sub_4_2": {"prereqs": ["Sub_4_1"], "coreqs": [], "antireqs": []},
    "Sub_4_3": {"prereqs": ["Sub_3_1", "Sub_2_5"], "coreqs": [], "antireqs": []},
    "Sub_4_4": {"prereqs": ["Sub_3_15", "Sub_3_4"], "coreqs": [], "antireqs": []},
    "Sub_4_5": {"prereqs": ["Sub_3_8"], "coreqs": [], "antireqs": []},
    "Sub_4_6": {"prereqs": ["Sub_3_4"], "coreqs": [], "antireqs": ["Sub_4_13"]},
    "Sub_4_7": {"prereqs": ["Sub_3_5", "Sub_2_3"], "coreqs": [], "antireqs": []},
    "Sub_4_8": {"prereqs": ["Sub_3_8", "Sub_3_12"], "coreqs": [], "antireqs": []},
    "Sub_4_9": {"prereqs": ["Sub_3_9", "Sub_3_6"], "coreqs": [], "antireqs": []},
    "Sub_4_10": {"prereqs": ["Sub_3_2"], "coreqs": [], "antireqs": []},
    "Sub_4_11": {"prereqs": ["Sub_4_1"], "coreqs": [], "antireqs": []},
    "Sub_4_12": {"prereqs": ["Sub_2_7"], "coreqs": [], "antireqs": []},
    "Sub_4_13": {"prereqs": ["Sub_2_3"], "coreqs": [], "antireqs": ["Sub_4_6"]},
    "Sub_4_14": {"prereqs": ["Sub_3_11"], "coreqs": [], "antireqs": []},
    "Sub_4_15": {"prereqs": ["Sub_3_3", "Sub_3_1"], "coreqs": [], "antireqs": []},
}


@router.get(
    "/curriculum",
    response_model=CurriculumGraphResponse,
    summary="Get complete Curriculum Knowledge Graph",
    description="Returns nodes (courses) and directed edges (prerequisites, co-requisites, anti-requisites) formatted for React Flow or D3.js."
)
def get_curriculum_graph(db: sqlite3.Connection = Depends(get_db)):
    """
    Fetches all 60 courses as nodes and builds graph edges based on
    prerequisite, co-requisite, and anti-requisite relationships.
    """
    try:
        raw_subjects = get_all_subjects(db)

        # 1. Build Nodes Array
        nodes: List[GraphNode] = []
        catalog_ids = set()

        for sub in raw_subjects:
            subj_id = sub["subject_id"]
            catalog_ids.add(subj_id)
            nodes.append(
                GraphNode(
                    id=subj_id,
                    label=sub["subject_name"],
                    semester=int(sub["semester"]),
                    credits=int(sub["credits"])
                )
            )

        # 2. Build Directed Edges Array
        edges: List[GraphEdge] = []
        seen_edges: Set[str] = set()

        for target_id, rules in CURRICULUM_DEPENDENCIES.items():
            if target_id not in catalog_ids:
                continue

            # A. Prerequisite Edges (source -> target : "Requires")
            for prereq_id in rules.get("prereqs", []):
                edge_id = f"e_{prereq_id}-{target_id}"
                if edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    edges.append(
                        GraphEdge(
                            id=edge_id,
                            source=prereq_id,
                            target=target_id,
                            type="prerequisite",
                            label="Requires"
                        )
                    )

            # B. Co-requisite Edges (source -> target : "Taken Together")
            for coreq_id in rules.get("coreqs", []):
                edge_id = f"e_{coreq_id}-{target_id}"
                if edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    edges.append(
                        GraphEdge(
                            id=edge_id,
                            source=coreq_id,
                            target=target_id,
                            type="corequisite",
                            label="Taken Together"
                        )
                    )

            # C. Anti-requisite Edges (source -> target : "Mutually Exclusive")
            for antireq_id in rules.get("antireqs", []):
                pair = tuple(sorted([target_id, antireq_id]))
                edge_id = f"e_{pair[0]}-{pair[1]}_antireq"
                if edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    edges.append(
                        GraphEdge(
                            id=edge_id,
                            source=pair[0],
                            target=pair[1],
                            type="antirequisite",
                            label="Mutually Exclusive"
                        )
                    )

        return CurriculumGraphResponse(
            nodes=nodes,
            edges=edges
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate curriculum knowledge graph: {str(e)}"
        )
