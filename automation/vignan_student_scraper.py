"""
Vignan University ERP Student Portal Web Scraper
=================================================
Target: https://erp.vignan.ac.in/student/

Authenticates a student using their Registration Number and Password,
logs into the portal, and extracts:
- regno: Student Registration Number
- name: Student Full Name
- cgpa: Cumulative Grade Point Average
- semester: Current Academic Semester
- department: Academic Branch / Department

Usage:
  1. CLI interactive prompt:
     python automation/vignan_student_scraper.py

  2. Command line arguments:
     python automation/vignan_student_scraper.py --regno 241FA04E95 --password YOUR_PASSWORD --mode Student

  3. Import as a Python module:
     from automation.vignan_student_scraper import scrape_vignan_student
     result = scrape_vignan_student("241FA04E95", "YOUR_PASSWORD")
"""

import sys
import re
import json
import argparse
import getpass
from typing import Dict, Any, Optional

import requests
import urllib3
from bs4 import BeautifulSoup

# Suppress SSL warnings for legacy university portals
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VignanERPScraper:
    """
    Client for scraping student academic data from Vignan University ERP (VFSTR).
    """

    BASE_URL = "https://erp.vignan.ac.in/student/"
    LOGIN_URL = "https://erp.vignan.ac.in/student/login1.jsp"
    PROFILE_URL = "https://erp.vignan.ac.in/student/profile.jsp"
    REPORT_URL = "https://erp.vignan.ac.in/student/reportall.jsp"
    FINAL_MARKS_URL = "https://erp.vignan.ac.in/student/finalmarks1.jsp"
    MID_MARKS_URL = "https://erp.vignan.ac.in/student/stumidmarks1.jsp"
    ATTENDANCE_URL = "https://erp.vignan.ac.in/student/attendance.jsp"
    FEES_URL = "https://erp.vignan.ac.in/student/stufeedetails1.jsp"

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://erp.vignan.ac.in",
        "Referer": "https://erp.vignan.ac.in/student/signin.jsp",
        "Connection": "keep-alive",
    }

    # Department code lookup table based on registration number patterns
    DEPT_LOOKUP = {
        "01": "Civil Engineering (CIVIL)",
        "02": "Electrical & Electronics Engineering (EEE)",
        "03": "Mechanical Engineering (MECH)",
        "04": "Computer Science & Engineering (CSE)",
        "05": "Electronics & Communication Engineering (ECE)",
        "06": "Chemical Engineering (CHEM)",
        "07": "Information Technology (IT)",
        "08": "Biotechnology (BT)",
        "12": "Information Technology (IT)",
        "19": "Computer Science & Engineering - AI & ML (AIML)",
        "20": "Computer Science & Engineering - Cyber Security (CSCS)",
        "21": "Computer Science & Engineering - Data Science (CSDS)",
        "22": "Computer Science & Engineering - IoT (CSIOT)",
    }

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.session.verify = False

    def login_and_scrape(self, regno: str, password: str, usertype: str = "Student") -> Dict[str, Any]:
        """
        Submits student credentials to Vignan ERP, handles session lifecycle,
        and parses student academic profile.
        """
        clean_regno = str(regno).strip().upper()
        clean_password = str(password).strip() if password else clean_regno
        clean_usertype = str(usertype).strip().capitalize() or "Student"

        if not clean_regno:
            return {
                "success": False,
                "error": "Registration number cannot be empty."
            }

        # Step 1: Initialize session and obtain session cookies
        try:
            init_res = self.session.get(self.BASE_URL, timeout=self.timeout)
            init_cookies = self.session.cookies.get_dict()
        except Exception as e:
            # Network issue connecting to portal
            return {
                "success": False,
                "error": f"Failed to connect to Vignan ERP ({self.BASE_URL}): {e}"
            }

        # Step 2: Post login credentials
        payload = {
            "user": clean_regno,
            "pwd": clean_password,
            "usertype": clean_usertype
        }

        try:
            login_res = self.session.post(
                self.LOGIN_URL,
                data=payload,
                timeout=self.timeout,
                allow_redirects=True
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Login POST request failed: {e}"
            }

        if login_res.status_code != 200:
            return {
                "success": False,
                "error": f"Vignan ERP returned HTTP {login_res.status_code}"
            }

        html_text = login_res.text
        lower_html = html_text.lower()

        # Step 3: Check for authentication errors in response
        if "worng password" in lower_html or "wrong password" in lower_html or "registerno not exists" in lower_html or "invalid" in lower_html:
            if "profile.jsp" not in lower_html and "logout" not in lower_html:
                return {
                    "success": False,
                    "error": f"Authentication failed on Vignan ERP for '{clean_regno}' in {clean_usertype} mode. Please verify Registration Number and Password."
                }

        # Step 4: Scrape student data from available pages
        profile_data = self._scrape_profile()
        report_data = self._scrape_report_all()
        marks_data = self._scrape_marks()
        attendance_data = self._scrape_attendance()

        # Step 5: Synthesize and normalize the 5 required fields
        # 1. RegNo
        final_regno = profile_data.get("regno") or report_data.get("regno") or clean_regno

        # 2. Name
        final_name = (
            profile_data.get("name")
            or report_data.get("name")
            or self._extract_name_from_html(html_text)
            or f"Student ({clean_regno})"
        )

        # 3. CGPA
        final_cgpa = (
            marks_data.get("cgpa")
            or report_data.get("cgpa")
            or profile_data.get("cgpa")
            or 0.0
        )

        # 4. Semester
        final_semester = (
            profile_data.get("semester")
            or report_data.get("semester")
            or self._calculate_semester_from_regno(clean_regno)
        )

        # 5. Department
        raw_dept = (
            profile_data.get("department")
            or report_data.get("department")
            or self._derive_department_from_regno(clean_regno)
        )
        final_department = self._format_department_name(raw_dept)

        # Derive structured fields from the registration number
        dept_code = self._extract_dept_code(clean_regno)
        year_of_join = self._extract_year_of_join(clean_regno)
        profile_section = profile_data.get("section", "")
        section = self._extract_section(clean_regno, profile_section)

        # Format output — all requested fields at the top level
        student_info = {
            # Identity
            "regno": final_regno,
            "name": final_name,
            # Registration number breakdown
            "year_of_join": year_of_join,        # e.g. "2024"
            "dept_code": dept_code,               # e.g. "04"
            # Academic info
            "department": final_department,
            "cgpa": float(final_cgpa) if final_cgpa else 0.0,
            "semester": int(final_semester),
            "section": section,                   # e.g. "E"
            # Supplementary
            "attendance_percentage": attendance_data.get("aggregate_percentage", 0.0),
            "enrolled_subjects_count": len(attendance_data.get("subjects", [])),
            "father_name": profile_data.get("father_name") or report_data.get("father_name", ""),
            "regulation": profile_data.get("regulation", "R22"),
        }

        return {
            "success": True,
            "source": "https://erp.vignan.ac.in/student/",
            "data": student_info
        }

    # -----------------------------------------------------------------------
    # Internal page scrapers & parsers
    # -----------------------------------------------------------------------
    @staticmethod
    def _parse_roman_or_digit(val: str) -> int:
        """Converts Roman numerals (I, II, III, IV) or strings ('1', '2', 'first') to int"""
        v = str(val).strip().upper()
        roman_map = {
            "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
            "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
            "1ST": 1, "2ND": 2, "3RD": 3, "4TH": 4
        }
        for k, num in roman_map.items():
            if v == k or re.search(rf"\b{k}\b", v):
                return num
        return 0

    def _calculate_true_semester(self, year_str: Optional[str], sem_str: Optional[str], full_context: str = "") -> int:
        """
        Calculates the true semester (1-8) from Year & Semester combinations.
        Example: Year II + Sem I -> Sem 3, Year II + Sem II -> Sem 4, Compound '3-1' -> Sem 5.
        """
        # 1. Search for compound patterns like '2-2', 'II/II', '3-1', '3/1', 'III-I'
        for text in [sem_str, year_str, full_context]:
            if not text:
                continue
            comp = re.search(r"\b(IV|III|II|I|[1-4])\s*[\-\/\_]\s*(II|I|[1-2])\b", str(text), re.I)
            if comp:
                y = self._parse_roman_or_digit(comp.group(1))
                s = self._parse_roman_or_digit(comp.group(2))
                if y >= 1 and s >= 1:
                    return (y - 1) * 2 + s

        # 2. Both Year and Semester parsed separately
        y_num = self._parse_roman_or_digit(year_str) if year_str else 0
        s_num = self._parse_roman_or_digit(sem_str) if sem_str else 0

        if y_num >= 1 and s_num in [1, 2]:
            return (y_num - 1) * 2 + s_num

        # 3. Direct semester number 1-8
        if s_num in range(1, 9):
            return s_num

        return 0

    def _scrape_profile(self) -> Dict[str, Any]:
        """Scrapes profile.jsp"""
        try:
            r = self.session.get(self.PROFILE_URL, timeout=self.timeout)
            if r.status_code == 200 and "signin.jsp" not in r.text.lower():
                return self._parse_profile_html(r.text)
        except Exception:
            pass
        return {}

    def _parse_profile_html(self, html: str) -> Dict[str, Any]:
        """Parses HTML of profile.jsp"""
        data = {}
        soup = BeautifulSoup(html, "html.parser")
        raw_year = None
        raw_sem = None

        tables = soup.find_all("table")
        for table in tables:
            for row in table.find_all("tr"):
                cols = row.find_all(["td", "th"])
                if len(cols) >= 2:
                    k = cols[0].get_text(strip=True).lower().replace(":", "")
                    v = cols[1].get_text(strip=True)
                    if "name" in k and "father" not in k and "mother" not in k:
                        data["name"] = v
                    elif "father" in k:
                        data["father_name"] = v
                    elif "branch" in k or "dept" in k or "programme" in k:
                        data["department"] = v
                    elif "year" in k:
                        raw_year = v
                    elif "semester" in k or "sem" in k:
                        raw_sem = v
                    elif "section" in k or "sec" in k:
                        data["section"] = v
                    elif "reg" in k:
                        data["regno"] = v

        computed_sem = self._calculate_true_semester(raw_year, raw_sem, html)
        if computed_sem:
            data["semester"] = computed_sem

        return data

    def _scrape_report_all(self) -> Dict[str, Any]:
        """Scrapes reportall.jsp"""
        try:
            r = self.session.get(self.REPORT_URL, timeout=self.timeout)
            if r.status_code == 200 and "signin.jsp" not in r.text.lower():
                return self._parse_report_all_html(r.text)
        except Exception:
            pass
        return {}

    def _parse_report_all_html(self, html: str) -> Dict[str, Any]:
        """Parses HTML of reportall.jsp"""
        data = {}
        soup = BeautifulSoup(html, "html.parser")
        raw_year = None
        raw_sem = None

        for tr in soup.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            if len(tds) >= 2:
                k = tds[0].get_text(strip=True).lower().replace(":", "")
                v = tds[1].get_text(strip=True)
                if "name" in k and "father" not in k and "mother" not in k:
                    data["name"] = v
                elif "branch" in k or "dept" in k:
                    data["department"] = v
                elif "year" in k:
                    raw_year = v
                elif "semester" in k or "sem" in k:
                    raw_sem = v

        computed_sem = self._calculate_true_semester(raw_year, raw_sem, html)
        if computed_sem:
            data["semester"] = computed_sem

        # Parse CGPA from tables/content
        cgpa_val = self._parse_cgpa_from_html(html)
        if cgpa_val:
            data["cgpa"] = cgpa_val

        return data

    def _scrape_marks(self) -> Dict[str, Any]:
        """Scrapes finalmarks1.jsp and stumidmarks1.jsp for CGPA and grades"""
        marks = {"cgpa": 0.0, "semester_results": []}
        for url in [self.FINAL_MARKS_URL, self.REPORT_URL, self.MID_MARKS_URL]:
            try:
                r = self.session.get(url, timeout=self.timeout)
                if r.status_code == 200 and "signin.jsp" not in r.text.lower():
                    parsed = self._parse_marks_html(r.text)
                    if parsed.get("cgpa"):
                        marks["cgpa"] = parsed["cgpa"]
                        if parsed.get("semester_count"):
                            marks["semester_count"] = parsed["semester_count"]
                        break
            except Exception:
                pass
        return marks

    def _parse_marks_html(self, html: str) -> Dict[str, Any]:
        """Parses CGPA from marks HTML page"""
        cgpa_val = self._parse_cgpa_from_html(html)
        
        # Count completed semesters in marks tables
        sem_matches = re.findall(r"(?:semester|sem)\s*[:\-]?\s*([I|V|X|1-8]+)", html, re.I)
        sem_count = len(set(sem_matches)) if sem_matches else 0

        return {
            "cgpa": cgpa_val,
            "semester_count": sem_count
        }

    def _parse_cgpa_from_html(self, html: str) -> float:
        """
        Extracts the most recent official CGPA from marks tables or summary indicators.
        Avoids picking up historical past semester 1 CGPA.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Strategy 1: Table column-based parsing
        table_cgpas = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            cgpa_col_idx = -1
            for row in rows:
                headers = [th.get_text(strip=True).lower() for th in row.find_all(["th", "td"])]
                for idx, h in enumerate(headers):
                    if "cgpa" in h or "cumulative" in h:
                        cgpa_col_idx = idx
                        break

                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if cgpa_col_idx != -1 and len(cells) > cgpa_col_idx:
                    val = cells[cgpa_col_idx]
                    m = re.search(r"^[0-9]+\.[0-9]+$", val)
                    if m:
                        f = float(m.group())
                        if 0.0 < f <= 10.0:
                            table_cgpas.append(f)

        if table_cgpas:
            return table_cgpas[-1]  # Return latest semester CGPA

        # Strategy 2: Explicit Overall / Total CGPA labels
        priority_patterns = [
            r"(?:Overall|Total|Cumulative|Final)\s*(?:Grade\s*Point\s*Average|GPA|CGPA)[\s\:\=\-\(]*([0-9]+\.[0-9]+)",
            r"(?:CGPA|Cumulative\s+GPA)[\s\:\=\-\(]*([0-9]+\.[0-9]+)"
        ]
        for pattern in priority_patterns:
            matches = re.findall(pattern, html, re.I)
            if matches:
                valid = [float(x) for x in matches if 0.0 < float(x) <= 10.0]
                if valid:
                    return valid[-1]

        # Strategy 3: General CGPA / SGPA regex list, take last valid value
        all_matches = re.findall(r"(?:CGPA|Cumulative\s+GPA|GPA)[\s\(\):=\-]*([0-9]+\.[0-9]+)", html, re.I)
        valid = [float(x) for x in all_matches if 0.0 < float(x) <= 10.0]
        if valid:
            return valid[-1]

        return 0.0

    def _scrape_attendance(self) -> Dict[str, Any]:
        """Scrapes attendance.jsp"""
        try:
            r = self.session.get(self.ATTENDANCE_URL, timeout=self.timeout)
            if r.status_code == 200 and "signin.jsp" not in r.text.lower():
                return self._parse_attendance_html(r.text)
        except Exception:
            pass
        return {"subjects": [], "aggregate_percentage": 0.0}

    def _parse_attendance_html(self, html: str) -> Dict[str, Any]:
        """Parses attendance HTML table"""
        result = {"subjects": [], "aggregate_percentage": 0.0}
        soup = BeautifulSoup(html, "html.parser")
        subjects = []
        for row in soup.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) >= 3:
                for cell in cells:
                    if "%" in cell or re.match(r"^\d+(\.\d+)?$", cell):
                        try:
                            val = float(cell.replace("%", "").strip())
                            if 0.0 <= val <= 100.0:
                                subjects.append({"percentage": val})
                                break
                        except ValueError:
                            pass
        if subjects:
            avg_att = round(sum(s["percentage"] for s in subjects) / len(subjects), 2)
            result["subjects"] = subjects
            result["aggregate_percentage"] = avg_att
        return result

    def _extract_name_from_html(self, html: str) -> Optional[str]:
        """Extracts student name from welcome headers if profile table is empty"""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "span", "b"]):
            text = tag.get_text(strip=True)
            if "welcome" in text.lower():
                cleaned = re.sub(r"welcome|student|[:\-]|mr\.|ms\.", "", text, flags=re.I).strip()
                if len(cleaned) > 2 and not cleaned.isdigit():
                    return cleaned
        return None

    def _calculate_semester_from_regno(self, regno: str) -> int:
        """Estimates current semester from Vignan registration number year prefix (e.g. 24 -> Sem 2)"""
        if len(regno) >= 2 and regno[:2].isdigit():
            year_prefix = regno[:2]
            sem_map = {"24": 2, "23": 4, "22": 6, "21": 8}
            return sem_map.get(year_prefix, 2)
        return 2

    def _derive_department_from_regno(self, regno: str) -> str:
        """Derives department from the middle branch code in the registration number (e.g. 241FA04E95 -> '04' -> CSE)"""
        match = re.search(r"FA(\d{2})", regno)
        if match:
            code = match.group(1)
            if code in self.DEPT_LOOKUP:
                return self.DEPT_LOOKUP[code]
        # Fallback keyword checks
        for code, name in self.DEPT_LOOKUP.items():
            if code in regno:
                return name
        return "Computer Science & Engineering (CSE)"

    def _extract_dept_code(self, regno: str) -> str:
        """Extracts the 2-digit department code from a Vignan registration number.
        Example: 241FA04424 -> '04'"""
        match = re.search(r"FA(\d{2})", regno.upper())
        return match.group(1) if match else ""

    def _extract_year_of_join(self, regno: str) -> str:
        """Extracts the 4-digit year of joining from the 2-digit prefix.
        Example: 241FA04424 -> '2024', 231FA19B01 -> '2023'"""
        if len(regno) >= 2 and regno[:2].isdigit():
            return "20" + regno[:2]
        return ""

    def _extract_section(self, regno: str, profile_section: str = "") -> str:
        """Returns section from profile data if available, otherwise derives it from
        the letter in the roll sequence of the registration number.
        Example: 241FA04E95 -> 'E'"""
        if profile_section:
            return profile_section
        # Roll number letter: last segment like E95, A01, B12
        match = re.search(r"([A-Z])\d{2}$", regno.upper())
        return match.group(1) if match else ""

    def _format_department_name(self, raw_dept: str) -> str:
        """Formats department names to clean standardized representation"""
        upper = raw_dept.upper()
        if "ARTIFICIAL" in upper or "AIML" in upper:
            return "Computer Science & Engineering - AI & ML (AIML)"
        elif "CYBER" in upper or "CSCS" in upper:
            return "Computer Science & Engineering - Cyber Security (CSCS)"
        elif "INFORMATION" in upper or "IT" in upper:
            return "Information Technology (IT)"
        elif "MECHANICAL" in upper or "MECH" in upper:
            return "Mechanical Engineering (MECH)"
        elif "CIVIL" in upper:
            return "Civil Engineering (CIVIL)"
        elif "ELECTRONICS" in upper or "ECE" in upper:
            return "Electronics & Communication Engineering (ECE)"
        elif "ELECTRICAL" in upper or "EEE" in upper:
            return "Electrical & Electronics Engineering (EEE)"
        elif "COMPUTER" in upper or "CSE" in upper:
            return "Computer Science & Engineering (CSE)"
        return raw_dept


def scrape_vignan_student(regno: str, password: Optional[str] = None, usertype: str = "Student") -> Dict[str, Any]:
    """
    Helper function to scrape student info from Vignan ERP portal.
    """
    scraper = VignanERPScraper()
    return scraper.login_and_scrape(regno, password or regno, usertype)


def main():
    parser = argparse.ArgumentParser(description="Scrape student information from Vignan University ERP portal.")
    parser.add_argument("--regno", "-r", type=str, help="Student Registration Number (e.g., 241FA04E95)")
    parser.add_argument("--password", "-p", type=str, help="Student Portal Password")
    parser.add_argument("--mode", "-m", type=str, default="Student", choices=["Student", "Parent", "Staff"], help="User Mode (default: Student)")
    parser.add_argument("--json", action="store_true", help="Output only raw JSON")

    args = parser.parse_args()

    regno = args.regno
    password = args.password
    mode = args.mode

    if not regno:
        print("=" * 60)
        print("   VIGNAN UNIVERSITY ERP STUDENT PORTAL SCRAPER")
        print("   Target: https://erp.vignan.ac.in/student/")
        print("=" * 60)
        regno = input("Enter Student Registration Number: ").strip()
        if not password:
            entered_pwd = getpass.getpass("Enter Password (press Enter to use Registration No): ").strip()
            password = entered_pwd if entered_pwd else regno

    if not password:
        password = regno

    if not args.json:
        print(f"\n[*] Connecting to https://erp.vignan.ac.in/student/ ...")
        print(f"[*] Submitting credentials for: {regno.upper()} (Mode: {mode}) ...\n")

    result = scrape_vignan_student(regno, password, mode)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if result.get("success"):
        data = result["data"]
        print("=" * 60)
        print("           STUDENT ACADEMIC INFORMATION")
        print("=" * 60)
        print(f"  Registration No : {data['regno']}")
        print(f"  Year of Joining : {data['year_of_join']}")
        print(f"  Dept Code       : {data['dept_code']}")
        print(f"  Student Name    : {data['name']}")
        print(f"  Department      : {data['department']}")
        print(f"  Section         : {data['section']}")
        print(f"  Current Semester: {data['semester']}")
        print(f"  CGPA            : {data['cgpa']}")
        print("-" * 60)
        print(f"  Attendance Pct  : {data.get('attendance_percentage', 0.0)}%")
        print(f"  Enrolled Courses: {data.get('enrolled_subjects_count', 0)}")
        print(f"  Father Name     : {data.get('father_name', '')}")
        print(f"  Regulation      : {data.get('regulation', 'R22')}")
        print("=" * 60)
        print("\nStructured JSON Data:")
        print(json.dumps(data, indent=2))
    else:
        print("=" * 60)
        print("[-] LOGIN / SCRAPING FAILED")
        print("=" * 60)
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
