"""
The Archivist (Agent 06) - Nightly Data Sync Engine
Autonomous backend microservice for idempotent ingestion and database synchronization.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List

class Agent6Archivist:
    """
    Agent 06: The Archivist
    Ingests daily delta payloads. Strictly idempotent. Atomic execution. Silent JSON output.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to backend/university.db
            self.db_path = Path(__file__).resolve().parent.parent / "backend" / "university.db"
        else:
            self.db_path = Path(db_path)

    def process_delta(self, payload: Dict[str, Any]) -> str:
        """
        Main pipeline: Ingest -> SQL Upsert -> Graph Upsert -> Verify/Commit -> Report
        Returns ONLY the strict JSON execution log.
        """
        response = {
            "sync_status": "FAILED",
            "records_processed": {
                "sql_rows_upserted": 0,
                "graph_nodes_merged": 0,
                "graph_edges_merged": 0
            },
            "errors": []
        }

        # 1. INGEST & VALIDATE
        student_updates = payload.get("Student_Updates", [])
        curriculum_updates = payload.get("Curriculum_Updates", [])
        
        valid_students = []
        for s in student_updates:
            # Basic schema validation
            if not isinstance(s.get("RegNo"), str) or not s["RegNo"]:
                response["errors"].append(f"Invalid Student Record: Missing RegNo - {s}")
                continue
            valid_students.append(s)

        valid_curriculum = []
        for c in curriculum_updates:
            if not isinstance(c.get("SubjectID"), str) or not c["SubjectID"]:
                response["errors"].append(f"Invalid Curriculum Record: Missing SubjectID - {c}")
                continue
            valid_curriculum.append(c)

        # 2. SQL UPSERT & 3. GRAPH UPSERT (Atomic Execution)
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Start explicit transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # --- 2. SQL UPSERT (State Data) ---
            for student in valid_students:
                reg_no = student.get("RegNo")
                cgpa = student.get("CGPA")
                goal = student.get("Goal")
                
                # Upsert query avoiding destructive overwrites (COALESCE)
                cursor.execute("""
                    INSERT INTO Students (RegNo, StudentName, Semester, CGPA, Goal)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(RegNo) DO UPDATE SET 
                        CGPA = COALESCE(excluded.CGPA, Students.CGPA),
                        Goal = COALESCE(excluded.Goal, Students.Goal)
                """, (
                    reg_no, 
                    student.get("StudentName", "Unknown"), 
                    student.get("Semester", 1), 
                    cgpa, 
                    goal
                ))
                response["records_processed"]["sql_rows_upserted"] += 1

            # --- 3. GRAPH UPSERT (Policy Data) ---
            # Simulating Graph-RAG Upserts (Nodes and Edges)
            for course in valid_curriculum:
                subj_id = course.get("SubjectID")
                subj_name = course.get("SubjectName", "Unknown")
                credits = course.get("Credits", 3)
                semester = course.get("Semester", 1)
                
                # Mock Node Merging in our SQLite catalog as a proxy for the Graph Nodes
                cursor.execute("""
                    INSERT INTO Subjects (SubjectID, SubjectName, Semester, Credits)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(SubjectID) DO UPDATE SET
                        SubjectName = COALESCE(excluded.SubjectName, Subjects.SubjectName),
                        Credits = COALESCE(excluded.Credits, Subjects.Credits)
                """, (subj_id, subj_name, semester, credits))
                
                response["records_processed"]["graph_nodes_merged"] += 1
                
                # Simulate Prerequisite Edges creation (mock logic for the required schema output)
                prereqs = course.get("Prerequisites", [])
                for prereq in prereqs:
                    # In a real Neo4j setup, this would be: MERGE (a)-[:PREREQ_FOR]->(b)
                    response["records_processed"]["graph_edges_merged"] += 1

            # 4. VERIFY & COMMIT
            conn.commit()
            
            if response["errors"]:
                response["sync_status"] = "PARTIAL"
            else:
                response["sync_status"] = "SUCCESS"

        except Exception as e:
            if conn:
                conn.rollback()
            response["sync_status"] = "FAILED"
            response["errors"].append(f"Transaction Rolled Back due to Error: {str(e)}")
        finally:
            if conn:
                conn.close()

        # 5. REPORT
        return json.dumps(response, indent=2)


if __name__ == "__main__":
    # Test Payload execution
    archivist = Agent6Archivist()
    
    mock_payload = {
        "Student_Updates": [
            {
                "RegNo": "REG1001",
                "CGPA": 8.5,
                "Goal": "Senior Software Engineer"
                # Name and Semester omitted to test NO DESTRUCTIVE OVERWRITES
            },
            {
                "RegNo": "REG9999", # New student
                "StudentName": "New Data Student",
                "Semester": 1,
                "CGPA": 9.0,
                "Goal": "Data Scientist"
            },
            {
                # Malformed to test Error Logging
                "MissingRegNo": True 
            }
        ],
        "Curriculum_Updates": [
            {
                "SubjectID": "Sub_9_1",
                "SubjectName": "Advanced Quantum ML",
                "Semester": 4,
                "Credits": 4,
                "Prerequisites": ["Sub_4_1", "Sub_4_2"]
            }
        ]
    }
    
    print(archivist.process_delta(mock_payload))
