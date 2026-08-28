"""
Unit & Integration Test Suite for Vignan ERP Web Scraper
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.vignan_scraper import VignanERPScraper
from backend.database.database import get_db_connection
from backend.routes.erp import _sync_scraped_student_to_db


class TestVignanScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = VignanERPScraper()

    def test_scraper_initialization(self):
        self.assertIsNotNone(self.scraper.session)
        self.assertIn("erp.vignan.ac.in", self.scraper.LOGIN_URL)
        self.assertEqual(self.scraper.LOGIN_URL, "https://erp.vignan.ac.in/student/login1.jsp")

    def test_profile_html_parsing(self):
        sample_html = """
        <html>
            <body>
                <table>
                    <tr><td>Registration No:</td><td>211FA04001</td></tr>
                    <tr><td>Student Name:</td><td>Saketh Varma</td></tr>
                    <tr><td>Father Name:</td><td>Ravi Varma</td></tr>
                    <tr><td>Mother Name:</td><td>Lakshmi</td></tr>
                    <tr><td>Branch / Department:</td><td>Computer Science and Engineering</td></tr>
                    <tr><td>Semester:</td><td>4</td></tr>
                    <tr><td>Section:</td><td>CSE-A</td></tr>
                </table>
            </body>
        </html>
        """
        profile = self.scraper._parse_profile_html(sample_html)
        self.assertEqual(profile.get("student_name"), "Saketh Varma")
        self.assertEqual(profile.get("father_name"), "Ravi Varma")
        self.assertEqual(profile.get("semester"), 4)
        self.assertEqual(profile.get("section"), "CSE-A")

    def test_attendance_html_parsing(self):
        sample_html = """
        <html>
            <body>
                <table>
                    <tr><th>S.No</th><th>Subject Code</th><th>Subject Name</th><th>Held</th><th>Attended</th><th>Percentage</th></tr>
                    <tr><td>1</td><td>22CS201</td><td>Database Management Systems</td><td>40</td><td>36</td><td>90.0%</td></tr>
                    <tr><td>2</td><td>22CS206</td><td>Design and Analysis of Algorithms</td><td>38</td><td>32</td><td>84.2%</td></tr>
                    <tr><td>3</td><td>22CS207</td><td>Operating Systems & Architecture</td><td>42</td><td>38</td><td>90.4%</td></tr>
                </table>
            </body>
        </html>
        """
        att = self.scraper._parse_attendance_html(sample_html)
        self.assertEqual(len(att["subjects"]), 3)
        self.assertEqual(att["subjects"][0]["subject_code"], "22CS201")
        self.assertEqual(att["subjects"][0]["percentage"], 90.0)
        self.assertGreaterEqual(att["aggregate_percentage"], 88.0)

    def test_marks_html_parsing(self):
        sample_html = """
        <html>
            <body>
                <div>Cumulative Grade Point Average (CGPA) : 8.65</div>
                <table>
                    <tr><td>22CS201</td><td>A+</td><td>Pass</td></tr>
                    <tr><td>22CS206</td><td>A</td><td>Pass</td></tr>
                </table>
            </body>
        </html>
        """
        marks = self.scraper._parse_marks_html(sample_html)
        self.assertEqual(marks.get("cgpa"), 8.65)
        self.assertEqual(marks.get("backlogs_count"), 0)

    def test_branch_normalization(self):
        self.assertEqual(self.scraper._normalize_branch("Computer Science and Engineering"), "CSE")
        self.assertEqual(self.scraper._normalize_branch("Artificial Intelligence and Machine Learning"), "AIML")
        self.assertEqual(self.scraper._normalize_branch("Cyber Security and CS"), "CSCS")
        self.assertEqual(self.scraper._normalize_branch("Information Technology"), "IT")
        self.assertEqual(self.scraper._normalize_branch("Mechanical Engineering"), "MECH")
        self.assertEqual(self.scraper._normalize_branch("Civil Engineering"), "CIVIL")

    def test_db_sync(self):
        conn = get_db_connection()
        mock_student = {
            "reg_no": "TEST_SCRAPER_999",
            "student_name": "Test Scraped Student",
            "branch": "CSE",
            "semester": 4,
            "cgpa": 8.75,
            "goal": "AI Researcher"
        }
        _sync_scraped_student_to_db(conn, mock_student)
        
        cursor = conn.cursor()
        cursor.execute("SELECT RegNo, StudentName, CGPA, Semester FROM Students WHERE RegNo = ?;", ("TEST_SCRAPER_999",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["StudentName"], "Test Scraped Student")
        self.assertEqual(float(row["CGPA"]), 8.75)
        self.assertEqual(int(row["Semester"]), 4)
        
        # Cleanup
        cursor.execute("DELETE FROM Student_Subjects WHERE RegNo = ?;", ("TEST_SCRAPER_999",))
        cursor.execute("DELETE FROM Students WHERE RegNo = ?;", ("TEST_SCRAPER_999",))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    unittest.main()
