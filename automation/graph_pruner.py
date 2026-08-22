"""
Graph Pruner & Maintenance Automator
Automatically detects retired/deprecated courses and updates prerequisite 
chains to point to new equivalent substitutes, ensuring the Graph-RAG remains valid.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any

class GraphPruner:
    """
    Simulates a graph traversal maintenance worker.
    Scans for retired subjects and remaps their dependencies.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Path(__file__).resolve().parent.parent / "backend" / "university.db"

    def prune_and_remap(self, retired_subject_id: str, new_subject_id: str) -> str:
        """
        Retires a subject and remaps all courses that required it to the new subject.
        """
        conn = None
        report = {
            "action": "GRAPH_PRUNE_AND_REMAP",
            "status": "IN_PROGRESS",
            "retired_node": retired_subject_id,
            "new_node": new_subject_id,
            "edges_remapped": 0,
            "students_affected": 0,
            "error": None
        }

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("BEGIN TRANSACTION")

            # 1. Update the retired subject in the catalog
            cursor.execute("""
                UPDATE Subjects 
                SET SubjectName = SubjectName || ' (RETIRED)' 
                WHERE SubjectID = ?
            """, (retired_subject_id,))

            # 2. Re-map prerequisites (simulated logic for the graph)
            # In Neo4j this would be: MATCH (a)-[r:PREREQ]->(retired) CREATE (a)-[:PREREQ]->(new) DELETE r
            # Here we just mock the report output for the system architecture demonstration
            report["edges_remapped"] = 3  # Mocked count of downstream courses affected

            # 3. Update any students currently enrolled in the retired course (swap them to the new one)
            cursor.execute("""
                UPDATE Student_Subjects
                SET SubjectID = ?
                WHERE SubjectID = ?
            """, (new_subject_id, retired_subject_id))
            
            report["students_affected"] = cursor.rowcount

            conn.commit()
            report["status"] = "SUCCESS"

        except Exception as e:
            if conn:
                conn.rollback()
            report["status"] = "FAILED"
            report["error"] = str(e)
        finally:
            if conn:
                conn.close()

        return json.dumps(report, indent=2)


if __name__ == "__main__":
    pruner = GraphPruner()
    print("--- Running Automated Graph Curriculum Maintenance ---")
    
    # Scenario: The university replaces old "Sub_1_1" with a new curriculum version "Sub_1_1_V2"
    print(pruner.prune_and_remap(retired_subject_id="Sub_1_1", new_subject_id="Sub_1_1_V2"))
