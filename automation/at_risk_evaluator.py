"""
The "At-Risk" Batch Evaluator (Cron Automation Script)
======================================================
Proactive academic intervention engine. Periodically scans the SQLite database,
identifies every student with a GPA below 6.0 (AT_RISK standing), automatically
runs them through the 5-agent advising pipeline, and generates a structured batch
report and faculty email digest of "Academic Survival Plans".

Can be run as a one-shot batch cron job or as a daemon interval evaluator.
"""

import argparse
import asyncio
import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Set utf-8 encoding for standard outputs on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure current and parent directories are in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automation.orchestrator import run_advising

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("at_risk_batch_evaluator")

DEFAULT_DB_PATH = PROJECT_ROOT / "backend" / "university.db"
DEFAULT_OUTPUT_JSON = CURRENT_DIR / "at_risk_batch_report.json"
DEFAULT_OUTPUT_MD = CURRENT_DIR / "at_risk_batch_report.md"


class AtRiskBatchEvaluator:
    """
    Automated Batch Evaluator for At-Risk Students.
    Scans the DBMS, triggers the 5-agent advising pipeline, and compiles Academic Survival Plans.
    """

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        gpa_threshold: float = 6.0,
        output_json_path: Optional[Union[str, Path]] = None,
        output_md_path: Optional[Union[str, Path]] = None,
    ):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.gpa_threshold = float(gpa_threshold)
        self.output_json_path = Path(output_json_path) if output_json_path else DEFAULT_OUTPUT_JSON
        self.output_md_path = Path(output_md_path) if output_md_path else DEFAULT_OUTPUT_MD

    def get_db_connection(self) -> sqlite3.Connection:
        """Establishes a read-only SQLite connection to the university database."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"University database not found at {self.db_path}")
        
        try:
            db_uri = f"file:{self.db_path.as_posix()}?mode=ro"
            conn = sqlite3.connect(db_uri, uri=True)
        except Exception:
            conn = sqlite3.connect(str(self.db_path))
            
        conn.row_factory = sqlite3.Row
        return conn

    def scan_at_risk_students(self) -> List[Dict[str, Any]]:
        """
        Scans the SQLite database for all students with CGPA < threshold.
        Returns a list of student profile dictionaries.
        """
        logger.info(f"Scanning DBMS for students with CGPA < {self.gpa_threshold:.2f} at: {self.db_path}")
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    s.RegNo,
                    s.StudentName,
                    s.Semester,
                    s.CGPA,
                    s.Goal
                FROM Students s
                WHERE s.CGPA < ?
                ORDER BY s.CGPA ASC, s.Semester DESC;
            """, (self.gpa_threshold,))
            rows = cursor.fetchall()

            at_risk_students: List[Dict[str, Any]] = []
            for r in rows:
                reg_no = r["RegNo"]
                # Fetch enrolled subjects
                cursor.execute("""
                    SELECT 
                        sub.SubjectID, 
                        sub.SubjectName, 
                        sub.Credits, 
                        ss.EnrollmentDate
                    FROM Student_Subjects ss
                    JOIN Subjects sub ON ss.SubjectID = sub.SubjectID
                    WHERE ss.RegNo = ?
                    ORDER BY sub.SubjectID;
                """, (reg_no,))
                subjects = [dict(sub_row) for sub_row in cursor.fetchall()]
                total_credits = sum(s["Credits"] for s in subjects)

                at_risk_students.append({
                    "reg_no": r["RegNo"],
                    "student_name": r["StudentName"],
                    "semester": r["Semester"],
                    "cgpa": r["CGPA"],
                    "goal": r["Goal"],
                    "total_enrolled_credits": total_credits,
                    "enrolled_subjects": subjects,
                })

            logger.info(f"Scan complete: Found {len(at_risk_students)} at-risk student(s) requiring intervention.")
            return at_risk_students

        finally:
            conn.close()

    async def evaluate_single_student(self, student: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs an individual at-risk student through the 5-agent advising pipeline.
        """
        reg_no = student["reg_no"]
        name = student["student_name"]
        cgpa = student["cgpa"]
        sem = student["semester"]
        goal = student["goal"]

        intervention_query = f"Emergency Academic Recovery & Backlog Clearance for {goal}"
        logger.info(f"Triggering 5-agent pipeline for {name} ({reg_no}) - CGPA: {cgpa:.2f}...")

        pipeline_result = await run_advising(student_id=reg_no, user_query=intervention_query)

        # Assemble Academic Survival Plan card
        survival_plan = {
            "student_id": reg_no,
            "student_name": name,
            "current_semester": sem,
            "current_cgpa": cgpa,
            "career_goal": goal,
            "intervention_status": pipeline_result.get("status", "failed"),
            "academic_standing": "AT_RISK",
            "enrolled_credits": student["total_enrolled_credits"],
            "recovery_pathway": pipeline_result.get("final_plan", {}).get("semester_pathway", []),
            "bottlenecks": pipeline_result.get("pipeline_context", {}).get("matrix", {}).get("bottlenecks", []),
            "strategic_momentum_plan": pipeline_result.get("final_plan", {}).get("strategic_momentum_plan", ""),
            "executive_summary": pipeline_result.get("final_plan", {}).get("executive_summary", ""),
            "pipeline_context": pipeline_result.get("pipeline_context", {}),
        }

        if pipeline_result.get("status") == "failed":
            survival_plan["failure_reason"] = pipeline_result.get("reason", "Unknown pipeline error")
            logger.warning(f"Pipeline reported failure for {reg_no}: {survival_plan['failure_reason']}")

        return survival_plan

    async def run_batch_evaluation(self, save_reports: bool = True) -> Dict[str, Any]:
        """
        Executes batch evaluation for all at-risk students and generates faculty reports.
        """
        batch_start = datetime.now(timezone.utc)
        students = self.scan_at_risk_students()

        # Count total students in database
        total_students_in_db = 0
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Students;")
            total_students_in_db = cur.fetchone()[0]
            conn.close()
        except Exception:
            total_students_in_db = len(students)

        # Execute evaluations concurrently
        tasks = [self.evaluate_single_student(s) for s in students]
        plans = await asyncio.gather(*tasks)

        successful_plans = [p for p in plans if p.get("intervention_status") == "success"]
        failed_plans = [p for p in plans if p.get("intervention_status") != "success"]

        batch_end = datetime.now(timezone.utc)
        duration_sec = round((batch_end - batch_start).total_seconds(), 2)

        batch_report = {
            "report_metadata": {
                "batch_id": f"batch_at_risk_{batch_start.strftime('%Y%m%d_%H%M%S')}",
                "generated_at": batch_start.isoformat(),
                "duration_seconds": duration_sec,
                "gpa_threshold": self.gpa_threshold,
                "database_target": str(self.db_path),
            },
            "summary_metrics": {
                "total_students_scanned": total_students_in_db,
                "total_at_risk_identified": len(students),
                "at_risk_percentage": round((len(students) / max(total_students_in_db, 1)) * 100, 1),
                "successful_plans_generated": len(successful_plans),
                "failed_plans_count": len(failed_plans),
            },
            "survival_plans": plans,
        }

        if save_reports:
            self.save_reports(batch_report)

        return batch_report

    def format_faculty_markdown_digest(self, batch_report: Dict[str, Any]) -> str:
        """
        Formats the batch evaluation report into a clean, human-readable Markdown digest
        suitable for faculty advising committees and email distribution.
        """
        meta = batch_report["report_metadata"]
        metrics = batch_report["summary_metrics"]
        plans = batch_report["survival_plans"]

        lines = [
            "# Proactive Academic Intervention Report: At-Risk Batch Digest",
            f"**Generated:** {meta['generated_at']} | **Scan Criteria:** CGPA < {meta['gpa_threshold']:.2f} | **Batch ID:** `{meta['batch_id']}`",
            "",
            "## Executive Summary",
            f"- **Total Student Population Scanned:** {metrics['total_students_scanned']}",
            f"- **At-Risk Students Identified (CGPA < {meta['gpa_threshold']}):** {metrics['total_at_risk_identified']} ({metrics['at_risk_percentage']}%)",
            f"- **Actionable Survival Plans Generated:** {metrics['successful_plans_generated']}",
            f"- **Pipeline Execution Time:** {meta['duration_seconds']}s",
            "",
            "---",
            "",
            "## Student-by-Student Academic Survival Plans",
            "",
        ]

        for idx, plan in enumerate(plans, 1):
            reg_no = plan["student_id"]
            name = plan["student_name"]
            cgpa = plan["current_cgpa"]
            sem = plan["current_semester"]
            goal = plan["career_goal"]
            bottlenecks = ", ".join(plan["bottlenecks"]) if plan["bottlenecks"] else "None (Open Pathway)"

            lines.extend([
                f"### {idx}. {name} (`{reg_no}`)",
                f"- **Current Standing:** AT_RISK (CGPA: **{cgpa:.2f}** / 10.00)",
                f"- **Academic Level:** Semester {sem} | **Enrolled Credits:** {plan['enrolled_credits']}",
                f"- **Target Career Goal:** {goal}",
                f"- **Identified Prerequisite Bottlenecks:** `{bottlenecks}`",
                "",
                "#### Recommended Recovery Course Pathway (Matrix Agent 02):",
            ])

            if plan["recovery_pathway"]:
                for step in plan["recovery_pathway"]:
                    nodes_str = ", ".join(step["nodes_to_complete"])
                    credits = step["step_total_credits_or_effort"]
                    lines.append(f"  * **{step['step_label']}:** {nodes_str} ({credits} Credits)")
            else:
                lines.append("  * *Immediate course registration adjustment under faculty review.*")

            lines.extend([
                "",
                "#### Strategic Action & Momentum Plan (Vector Agent 03):",
                plan["strategic_momentum_plan"] or "*Plan synthesis pending faculty consultation.*",
                "",
                "---",
                "",
            ])

        lines.extend([
            "**Advising Protocol Action Required:** Faculty mentors are requested to review each student's recovery pathway before the upcoming registration deadline.",
            "*Generated automatically by the Anti Gravity Autonomous Advising Pipeline.*"
        ])

        return "\n".join(lines)

    def save_reports(self, batch_report: Dict[str, Any]) -> None:
        """Persists the JSON batch report and Markdown faculty digest to disk."""
        # 1. Save JSON Report
        self.output_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_json_path, "w", encoding="utf-8") as f:
            json.dump(batch_report, f, indent=2)
        logger.info(f"JSON batch report saved to: {self.output_json_path}")

        # 2. Save Markdown Digest
        md_content = self.format_faculty_markdown_digest(batch_report)
        with open(self.output_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info(f"Faculty Markdown digest saved to: {self.output_md_path}")


# ===========================================================================
# CRON & PERIODIC DAEMON RUNNER
# ===========================================================================

async def run_cron_scheduler(interval_seconds: int = 3600, threshold: float = 6.0, db_path: Path = DEFAULT_DB_PATH):
    """
    Runs the At-Risk Batch Evaluator on a recurring cron-style interval.
    """
    evaluator = AtRiskBatchEvaluator(db_path=db_path, gpa_threshold=threshold)
    logger.info(f"Starting At-Risk Cron Scheduler: running every {interval_seconds}s for CGPA < {threshold}...")

    iteration = 1
    while True:
        logger.info(f"--- [CRON TRIGGER #{iteration}] Starting Batch Evaluation ---")
        try:
            report = await evaluator.run_batch_evaluation(save_reports=True)
            logger.info(f"[CRON TRIGGER #{iteration}] Complete: {report['summary_metrics']['successful_plans_generated']} plans generated.")
        except Exception as e:
            logger.exception(f"[CRON TRIGGER #{iteration}] Encountered error during batch evaluation: {e}")

        logger.info(f"Sleeping for {interval_seconds} seconds until next scheduled evaluation...")
        await asyncio.sleep(interval_seconds)
        iteration += 1


async def main():
    """CLI entrypoint for running the At-Risk Batch Evaluator."""
    parser = argparse.ArgumentParser(
        description="The 'At-Risk' Batch Evaluator - Automated Cron Academic Intervention Engine."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=6.0,
        help="GPA threshold for AT_RISK categorization (default: 6.0)."
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(DEFAULT_DB_PATH),
        help="Path to the SQLite university database."
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=str(DEFAULT_OUTPUT_JSON),
        help="Path to save the output JSON report."
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default=str(DEFAULT_OUTPUT_MD),
        help="Path to save the output Markdown digest."
    )
    parser.add_argument(
        "--cron",
        action="store_true",
        help="Run continuously in recurring cron mode."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Interval in seconds between cron runs (default: 3600s / 1 hour)."
    )
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="Print the formatted faculty email digest to stdout."
    )

    args = parser.parse_args()

    evaluator = AtRiskBatchEvaluator(
        db_path=args.db,
        gpa_threshold=args.threshold,
        output_json_path=args.output_json,
        output_md_path=args.output_md
    )

    if args.cron:
        await run_cron_scheduler(
            interval_seconds=args.interval,
            threshold=args.threshold,
            db_path=Path(args.db)
        )
    else:
        report = await evaluator.run_batch_evaluation(save_reports=True)
        
        print("\n" + "=" * 80)
        print("          AT-RISK BATCH EVALUATOR: EXECUTION SUMMARY")
        print("=" * 80)
        print(f"  * Total Students Scanned        : {report['summary_metrics']['total_students_scanned']}")
        print(f"  * At-Risk Identified (GPA < {args.threshold}) : {report['summary_metrics']['total_at_risk_identified']}")
        print(f"  * Survival Plans Generated      : {report['summary_metrics']['successful_plans_generated']}")
        print(f"  * Output JSON Report            : {args.output_json}")
        print(f"  * Faculty Markdown Digest       : {args.output_md}")
        print("=" * 80)

        if args.print_digest or True:
            print("\n" + evaluator.format_faculty_markdown_digest(report))


if __name__ == "__main__":
    asyncio.run(main())
