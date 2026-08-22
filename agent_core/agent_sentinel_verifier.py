"""
Sentinel (Agent 06) - Formal Constraint Verification & Faculty Approval Engine
==============================================================================
Enforces mathematical constraint invariants across curriculum graphs,
evaluates graduation risk scores, checks academic standing rules,
and manages formal faculty waiver/overload petitions with immutable audit hashes.
"""

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .agent_schemas import (
        ConflictItem,
        ConflictDiagnosticReport,
        FacultyPetitionRecord,
        FacultyPetitionCreate,
    )
except ImportError:
    try:
        from agent_schemas import (
            ConflictItem,
            ConflictDiagnosticReport,
            FacultyPetitionRecord,
            FacultyPetitionCreate,
        )
    except ImportError:
        from schemas import (
            ConflictItem,
            ConflictDiagnosticReport,
            FacultyPetitionRecord,
            FacultyPetitionCreate,
        )

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "university.db"


class SentinelVerifierAgent:
    """
    Agent 6: Sentinel (Formal Constraint & Faculty Approval Engine).
    Verifies policy invariants, scores graduation bottlenecks, and manages faculty overrides.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def evaluate_student_conflicts_and_risks(
        self,
        student_id: str,
        student_profile: Dict[str, Any],
        enrolled_subject_ids: List[str],
        completed_subject_ids: List[str]
    ) -> ConflictDiagnosticReport:
        """
        Executes formal constraint checks on a student's enrolled courses and academic record.
        """
        conflicts: List[ConflictItem] = []
        cgpa = float(student_profile.get("cgpa", 7.5))
        semester = int(student_profile.get("semester", 1))
        enrolled_set = set(enrolled_subject_ids)
        completed_set = set(completed_subject_ids)

        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. Prerequisite Completeness Check for Enrolled Subjects
        cursor.execute("""
            SELECT p.SubjectID, p.PrereqSubjectID, p.PrereqType, s1.SubjectName as TargetName, s2.SubjectName as PrereqName
            FROM Prerequisites p
            JOIN Subjects s1 ON p.SubjectID = s1.SubjectID
            JOIN Subjects s2 ON p.PrereqSubjectID = s2.SubjectID;
        """)
        all_prereqs = cursor.fetchall()
        
        prereq_map = {}
        for r in all_prereqs:
            sid = r["SubjectID"]
            if sid not in prereq_map:
                prereq_map[sid] = []
            prereq_map[sid].append(dict(r))

        for sid in enrolled_set:
            if sid in prereq_map:
                for req in prereq_map[sid]:
                    req_type = req["PrereqType"]
                    req_prereq_id = req["PrereqSubjectID"]
                    target_name = req["TargetName"]
                    prereq_name = req["PrereqName"]

                    if req_type == "HARD_PREREQ":
                        if req_prereq_id not in completed_set and req_prereq_id not in enrolled_set:
                            conflicts.append(ConflictItem(
                                conflict_id=f"MISSING_PREREQ_{sid}_{req_prereq_id}",
                                conflict_type="PREREQUISITE_MISSING",
                                severity="CRITICAL",
                                affected_courses=[sid, req_prereq_id],
                                description=f"Course '{target_name}' ({sid}) requires prerequisite '{prereq_name}' ({req_prereq_id}) which has not been cleared.",
                                remedy_recommendation=f"Submit a Faculty Prerequisite Waiver Petition or complete '{prereq_name}' prior to enrolling.",
                                policy_citation="[Policy §3.1: Prerequisite Progression]"
                            ))

                    elif req_type == "COREQ":
                        if req_prereq_id not in completed_set and req_prereq_id not in enrolled_set:
                            conflicts.append(ConflictItem(
                                conflict_id=f"COREQ_MISMATCH_{sid}_{req_prereq_id}",
                                conflict_type="COREQUISITE_VIOLATION",
                                severity="WARNING",
                                affected_courses=[sid, req_prereq_id],
                                description=f"Course '{target_name}' ({sid}) is designated to be taken concurrently with '{prereq_name}' ({req_prereq_id}).",
                                remedy_recommendation=f"Register for '{prereq_name}' in the same term to ensure coordinated lab/lecture integration.",
                                policy_citation="[Policy §3.1: Prerequisite Progression]"
                            ))

                    elif req_type == "ANTIREQ":
                        if req_prereq_id in completed_set or req_prereq_id in enrolled_set:
                            conflicts.append(ConflictItem(
                                conflict_id=f"ANTIREQ_COLLISION_{sid}_{req_prereq_id}",
                                conflict_type="ANTIREQUISITE_COLLISION",
                                severity="CRITICAL",
                                affected_courses=[sid, req_prereq_id],
                                description=f"Mutual exclusion collision: '{target_name}' ({sid}) and '{prereq_name}' ({req_prereq_id}) are anti-requisite tracks.",
                                remedy_recommendation="Drop one of the mutually exclusive courses as dual graduation credits will not be awarded.",
                                policy_citation="[Policy §7.1: Anti-Requisite Exclusion]"
                            ))

        # 2. Credit Overload / Underload Checks
        cursor.execute("SELECT SubjectID, Credits FROM Subjects WHERE SubjectID IN ({})".format(
            ",".join("?" for _ in enrolled_subject_ids) if enrolled_subject_ids else "''"
        ), enrolled_subject_ids)
        enrolled_credit_rows = cursor.fetchall()
        total_term_credits = sum(r["Credits"] for r in enrolled_credit_rows)

        if total_term_credits > 20:
            if cgpa < 8.0:
                conflicts.append(ConflictItem(
                    conflict_id="CREDIT_OVERLOAD_UNAUTHORIZED",
                    conflict_type="CREDIT_OVERLOAD",
                    severity="CRITICAL",
                    affected_courses=enrolled_subject_ids,
                    description=f"Current term credit total of {total_term_credits} exceeds the standard 20-credit limit without required 8.0+ CGPA qualification (Current CGPA: {cgpa:.2f}).",
                    remedy_recommendation="Drop 1 course or submit a Faculty Credit Overload Petition with academic rationale.",
                    policy_citation="[Policy §2.1: Credit Load & Overload]"
                ))
            else:
                conflicts.append(ConflictItem(
                    conflict_id="CREDIT_OVERLOAD_HONORS",
                    conflict_type="CREDIT_OVERLOAD",
                    severity="INFO",
                    affected_courses=enrolled_subject_ids,
                    description=f"Enrolled in {total_term_credits} credits (Overload). Validated under Honors qualification (CGPA {cgpa:.2f} >= 8.00).",
                    remedy_recommendation="Maintain continuous progress across all courses to preserve Honors standing.",
                    policy_citation="[Policy §2.1: Credit Load & Overload]"
                ))

        # 3. GPA Probation Risk Check
        if cgpa < 6.0:
            conflicts.append(ConflictItem(
                conflict_id="ACADEMIC_PROBATION_RISK",
                conflict_type="GPA_PROBATION_RISK",
                severity="CRITICAL",
                affected_courses=[],
                description=f"Cumulative GPA of {cgpa:.2f} is below the 6.00 threshold, placing student in Academic Probation.",
                remedy_recommendation="Enrollment capped at 16 credits per semester. Mandatory bi-weekly academic counseling required.",
                policy_citation="[Policy §5.1: Academic Standing]"
            ))

        # 4. Capstone Eligibility Check for Upperclassmen
        if semester == 4 and "Sub_4_15" in enrolled_set:
            if "Sub_3_3" not in completed_set or "Sub_3_1" not in completed_set:
                conflicts.append(ConflictItem(
                    conflict_id="CAPSTONE_PREREQ_INCOMPLETE",
                    conflict_type="PREREQUISITE_MISSING",
                    severity="CRITICAL",
                    affected_courses=["Sub_4_15", "Sub_3_3", "Sub_3_1"],
                    description="Capstone Research (Sub_4_15) requires verified passing grades in both Algorithms (Sub_3_3) and DBMS (Sub_3_1).",
                    remedy_recommendation="Complete prerequisite foundation subjects or seek faculty project committee exemption.",
                    policy_citation="[Policy §6.1: Capstone Eligibility]"
                ))

        conn.close()

        critical_count = sum(1 for c in conflicts if c.severity == "CRITICAL")
        warning_count = sum(1 for c in conflicts if c.severity == "WARNING")
        
        risk_score = min(1.0, (critical_count * 0.35) + (warning_count * 0.15) + (0.4 if cgpa < 6.0 else 0.0))
        risk_score = round(risk_score, 2)

        has_conflicts = critical_count > 0 or warning_count > 0

        summary = (
            f"Diagnostics completed: {critical_count} critical conflict(s) and {warning_count} warning(s) detected. "
            f"Graduation Risk Index is evaluated at {risk_score * 100:.0f}%."
        ) if has_conflicts else (
            f"Constraint verification cleared: Zero prerequisite or credit conflicts detected. "
            f"Graduation Risk Index is optimal at {risk_score * 100:.0f}%."
        )

        return ConflictDiagnosticReport(
            student_id=student_id,
            has_conflicts=has_conflicts,
            critical_count=critical_count,
            warning_count=warning_count,
            conflicts=conflicts,
            graduation_risk_score=risk_score,
            summary=summary
        )

    def fetch_petitions_for_student(self, student_id: str) -> List[FacultyPetitionRecord]:
        """Retrieves all faculty petitions associated with a student."""
        if not self.db_path.exists():
            return []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    fp.PetitionID, fp.RegNo, st.StudentName,
                    fp.SubjectID, sb.SubjectName,
                    fp.PetitionType, fp.Reason, fp.Status,
                    fp.FacultyRemarks, fp.Timestamp, fp.AuditHash
                FROM Faculty_Petitions fp
                LEFT JOIN Students st ON fp.RegNo = st.RegNo
                LEFT JOIN Subjects sb ON fp.SubjectID = sb.SubjectID
                WHERE fp.RegNo = ?
                ORDER BY fp.Timestamp DESC;
            """, (student_id,))
            rows = cursor.fetchall()
            conn.close()

            records = []
            for r in rows:
                records.append(FacultyPetitionRecord(
                    petition_id=r["PetitionID"],
                    reg_no=r["RegNo"],
                    student_name=r["StudentName"],
                    subject_id=r["SubjectID"],
                    subject_name=r["SubjectName"],
                    petition_type=r["PetitionType"],
                    reason=r["Reason"],
                    status=r["Status"],
                    faculty_remarks=r["FacultyRemarks"],
                    timestamp=str(r["Timestamp"]),
                    audit_hash=r["AuditHash"]
                ))
            return records
        except Exception:
            return []

    def create_petition(self, payload: FacultyPetitionCreate) -> FacultyPetitionRecord:
        """Creates a new faculty petition with an immutable SHA-256 audit hash."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Faculty_Petitions;")
        count = cursor.fetchone()[0] + 1
        petition_id = f"PET_{1000 + count}"

        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        hash_seed = f"{petition_id}:{payload.reg_no}:{payload.subject_id}:{payload.petition_type}:{payload.reason}:{timestamp_str}"
        audit_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()

        cursor.execute("""
            INSERT INTO Faculty_Petitions (PetitionID, RegNo, SubjectID, PetitionType, Reason, Status, FacultyRemarks, AuditHash)
            VALUES (?, ?, ?, ?, ?, 'PENDING', NULL, ?);
        """, (petition_id, payload.reg_no, payload.subject_id, payload.petition_type, payload.reason, audit_hash))

        cursor.execute("SELECT StudentName FROM Students WHERE RegNo = ?;", (payload.reg_no,))
        st_row = cursor.fetchone()
        st_name = st_row[0] if st_row else "Unknown"

        cursor.execute("SELECT SubjectName FROM Subjects WHERE SubjectID = ?;", (payload.subject_id,))
        sb_row = cursor.fetchone()
        sb_name = sb_row[0] if sb_row else payload.subject_id

        conn.commit()
        conn.close()

        return FacultyPetitionRecord(
            petition_id=petition_id,
            reg_no=payload.reg_no,
            student_name=st_name,
            subject_id=payload.subject_id,
            subject_name=sb_name,
            petition_type=payload.petition_type,
            reason=payload.reason,
            status="PENDING",
            faculty_remarks=None,
            timestamp=timestamp_str,
            audit_hash=audit_hash
        )

    def process_faculty_action(self, petition_id: str, action: str, remarks: str) -> Optional[FacultyPetitionRecord]:
        """Approves or rejects a faculty petition and logs the remarks."""
        conn = self._get_connection()
        cursor = conn.cursor()

        new_status = "APPROVED" if action.upper() == "APPROVE" else "REJECTED"

        cursor.execute("""
            UPDATE Faculty_Petitions
            SET Status = ?, FacultyRemarks = ?
            WHERE PetitionID = ?;
        """, (new_status, remarks, petition_id))

        if cursor.rowcount == 0:
            conn.close()
            return None

        conn.commit()

        cursor.execute("""
            SELECT 
                fp.PetitionID, fp.RegNo, st.StudentName,
                fp.SubjectID, sb.SubjectName,
                fp.PetitionType, fp.Reason, fp.Status,
                fp.FacultyRemarks, fp.Timestamp, fp.AuditHash
            FROM Faculty_Petitions fp
            LEFT JOIN Students st ON fp.RegNo = st.RegNo
            LEFT JOIN Subjects sb ON fp.SubjectID = sb.SubjectID
            WHERE fp.PetitionID = ?;
        """, (petition_id,))
        r = cursor.fetchone()
        conn.close()

        if not r:
            return None

        return FacultyPetitionRecord(
            petition_id=r["PetitionID"],
            reg_no=r["RegNo"],
            student_name=r["StudentName"],
            subject_id=r["SubjectID"],
            subject_name=r["SubjectName"],
            petition_type=r["PetitionType"],
            reason=r["Reason"],
            status=r["Status"],
            faculty_remarks=r["FacultyRemarks"],
            timestamp=str(r["Timestamp"]),
            audit_hash=r["AuditHash"]
        )
