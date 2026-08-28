import unittest
from automation.vignan_student_scraper import VignanERPScraper


class TestVignanERPScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = VignanERPScraper()

    def test_department_lookup(self):
        dept = self.scraper._derive_department_from_regno("241FA04E95")
        self.assertIn("CSE", dept)
        dept_aiml = self.scraper._derive_department_from_regno("231FA19001")
        self.assertIn("AIML", dept_aiml)
        dept_ece = self.scraper._derive_department_from_regno("221FA05010")
        self.assertIn("ECE", dept_ece)

    def test_true_semester_calculation(self):
        # Year 2 Sem 2 -> Sem 4
        self.assertEqual(self.scraper._calculate_true_semester("II", "II"), 4)
        # Year 3 Sem 1 -> Sem 5
        self.assertEqual(self.scraper._calculate_true_semester("3", "1"), 5)
        # Compound 2-1 -> Sem 3
        self.assertEqual(self.scraper._calculate_true_semester("", "2-1"), 3)
        # Compound 4-2 -> Sem 8
        self.assertEqual(self.scraper._calculate_true_semester("", "4-2"), 8)

    def test_profile_html_parsing(self):
        mock_html = """
        <html>
            <body>
                <table>
                    <tr><td>Reg No:</td><td>241FA04E95</td></tr>
                    <tr><td>Name:</td><td>JOHN DOE</td></tr>
                    <tr><td>Branch:</td><td>Computer Science & Engineering</td></tr>
                    <tr><td>Year:</td><td>II</td></tr>
                    <tr><td>Semester:</td><td>II</td></tr>
                    <tr><td>Section:</td><td>CSE-E</td></tr>
                </table>
            </body>
        </html>
        """
        data = self.scraper._parse_profile_html(mock_html)
        self.assertEqual(data.get("regno"), "241FA04E95")
        self.assertEqual(data.get("name"), "JOHN DOE")
        self.assertEqual(data.get("department"), "Computer Science & Engineering")
        self.assertEqual(data.get("semester"), 4)  # Year II + Sem II = Sem 4
        self.assertEqual(data.get("section"), "CSE-E")

    def test_marks_html_cgpa_latest(self):
        mock_marks_html = """
        <html>
            <body>
                <table>
                    <tr><th>Semester</th><th>SGPA</th><th>CGPA</th></tr>
                    <tr><td>I-I</td><td>8.10</td><td>8.10</td></tr>
                    <tr><td>I-II</td><td>8.50</td><td>8.30</td></tr>
                    <tr><td>II-I</td><td>8.90</td><td>8.50</td></tr>
                    <tr><td>II-II</td><td>9.10</td><td>8.74</td></tr>
                </table>
            </body>
        </html>
        """
        data = self.scraper._parse_marks_html(mock_marks_html)
        self.assertEqual(data.get("cgpa"), 8.74)  # Must be latest semester 8.74, not 8.10!


if __name__ == "__main__":
    unittest.main()
