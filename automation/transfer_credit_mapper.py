"""
Transfer Credit Mapper - Automated Transcript Ingestion
Parses external university transcripts and maps them to internal courses for credit.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

class TransferCreditMapper:
    """
    Simulates an OCR + NLP mapping system.
    Takes an external transcript, matches external courses to internal Subjects,
    and grants the student the respective credits in the database.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Path(__file__).resolve().parent.parent / "backend" / "university.db"
        # Mock NLP matching threshold rules
        self.course_mapping_dictionary = {
            "CS101_EXT": "Sub_1_1",  # Intro to Programming -> Intro to CS
            "MATH200_EXT": "Sub_1_2", # Calc 1 -> Engineering Math
            "DB400_EXT": "Sub_3_1",  # Database Admin -> Database Management
        }

    def process_transcript(self, student_id: str, external_transcript: List[Dict[str, Any]]) -> str:
        conn = None
        results = {
            "student_id": student_id,
            "status": "PROCESSED",
            "credits_transferred": 0,
            "mapped_courses": [],
            "unmapped_courses": []
        }

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")

            for ext_course in external_transcript:
                ext_id = ext_course.get("external_id")
                ext_name = ext_course.get("course_name")
                grade = ext_course.get("grade")
                
                # Check if grade is passable (B or higher for transfer)
                if grade not in ["A", "B", "A+", "B+"]:
                    results["unmapped_courses"].append({
                        "course": ext_name,
                        "reason": f"Grade {grade} too low for transfer."
                    })
                    continue

                internal_id = self.course_mapping_dictionary.get(ext_id)
                if not internal_id:
                    results["unmapped_courses"].append({
                        "course": ext_name,
                        "reason": "No equivalent internal course found."
                    })
                    continue

                # Map to internal and insert into Student_Subjects
                cursor.execute("""
                    INSERT OR IGNORE INTO Student_Subjects (RegNo, SubjectID, EnrollmentDate)
                    VALUES (?, ?, date('now'))
                """, (student_id, internal_id))

                if cursor.rowcount > 0:
                    results["credits_transferred"] += ext_course.get("credits", 3)
                    results["mapped_courses"].append({
                        "external": ext_name,
                        "internal_id": internal_id
                    })

            # Commit
            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            results["status"] = "FAILED"
            results["error"] = str(e)
        finally:
            if conn:
                conn.close()

        return json.dumps(results, indent=2)


if __name__ == "__main__":
    mapper = TransferCreditMapper()
    
    mock_transcript = [
        {"external_id": "CS101_EXT", "course_name": "Introduction to Java", "grade": "A", "credits": 4},
        {"external_id": "MATH200_EXT", "course_name": "Calculus I", "grade": "B", "credits": 3},
        {"external_id": "ART101_EXT", "course_name": "Pottery", "grade": "A", "credits": 2}, # Unmapped
        {"external_id": "DB400_EXT", "course_name": "Relational DBs", "grade": "C", "credits": 4}, # Too low grade
    ]
    
    print("--- Running Automated Transfer Credit Mapper ---")
    print(mapper.process_transcript("REG1001", mock_transcript))
