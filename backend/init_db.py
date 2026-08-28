"""
University Academic Advising & Curriculum Database Initializer
=============================================================
A complete, standalone Python script using sqlite3 and random libraries
to create, format, and populate a local SQLite database (university.db).

Enhanced Schema:
1. Degree_Requirements: General catalog rules & graduation constraints.
2. Subjects: Full course catalog across branches & semesters with Branch & Credits.
3. Students: Realistic student records with CGPA, Semester, Career Goal, and Branch.
4. Student_Subjects: Enrolled courses per student (enforcing enrollment rules).
5. Prerequisites: Explicit graph edge table (HARD_PREREQ, COREQ, ANTIREQ).
6. Course_Equivalences: Approved course substitutions and alternate elective tracks.
7. Academic_Policies: Graph-RAG policy knowledge base with clause citations.
8. Faculty_Petitions & Waiver_Requests: Override, waiver, and exception workflow with audit hashes.
"""

import hashlib
import os
import random
import sqlite3
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union

try:
    from backend.pdf_curriculum_parser import load_cse_curriculum, assign_weighted_credits
except ImportError:
    from pdf_curriculum_parser import load_cse_curriculum, assign_weighted_credits

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "university.db"

CAREER_GOALS: List[str] = [
    "Data Scientist",
    "Software Engineer",
    "AI Researcher",
    "Cybersecurity Analyst",
    "Cloud Architect",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Full Stack Developer",
    "Systems Software Engineer",
    "Robotics & Embedded Systems Specialist",
]

FIRST_NAMES: List[str] = [
    "Aarav", "Aditi", "Alexander", "Ananya", "Benjamin", "Charlotte", "Daniel",
    "Diya", "Elena", "Ethan", "Fatima", "Gabriel", "Grace", "Hannah", "Ishaan",
    "James", "Jasmine", "Kavya", "Liam", "Lucas", "Maya", "Michael", "Nathan",
    "Neha", "Noah", "Olivia", "Priya", "Rahul", "Riya", "Rohan", "Samantha",
    "Sara", "Siddharth", "Sophia", "Tanya", "Varun", "Vikram", "William", "Zara", "Zoe"
]

LAST_NAMES: List[str] = [
    "Anderson", "Banerjee", "Brown", "Chen", "Choudhury", "Davis", "Deshmukh",
    "Garcia", "Gupta", "Iyer", "Johnson", "Kapoor", "Khan", "Kumar", "Lee",
    "Martin", "Miller", "Mukherjee", "Nair", "Patel", "Rao", "Reddy", "Rodriguez",
    "Sharma", "Smith", "Taylor", "Thomas", "Verma", "Walker", "Williams", "Wilson", "Zhang"
]

BRANCH_SUBJECTS_TEMPLATE: Dict[str, List[List[str]]] = {
    "AIML": [
        ["Intro to Python", "Engineering Math I", "Statistics & Probability", "Physics", "Communication Skills", "Engineering Workshop"],
        ["Data Structures", "Advanced Statistics", "Linear Algebra", "Data Mining", "Web Dev Fundamentals", "Environmental Science"],
        ["Machine Learning", "Deep Learning Foundations", "Database Systems", "AI Principles", "Data Visualization", "Natural Language Processing"],
        ["Computer Vision", "Reinforcement Learning", "Big Data Analytics", "MLOps", "Ethical AI", "Capstone Project"]
    ],
    "BBA": [
        ["Principles of Management", "Business Mathematics", "Microeconomics", "Business Communication", "Accounting Fundamentals", "IT for Business"],
        ["Marketing Management", "Macroeconomics", "Organizational Behavior", "Financial Management", "Business Law", "Environmental Science"],
        ["Human Resource Management", "Operations Management", "Business Research Methods", "Consumer Behavior", "Corporate Finance", "E-Commerce"],
        ["Strategic Management", "International Business", "Business Analytics", "Entrepreneurship", "FinTech", "Capstone Project"]
    ],
    "CSCS": [
        ["Intro to Programming", "Engineering Math I", "Digital Logic", "Physics", "Communication Skills", "Engineering Workshop"],
        ["Data Structures", "Object Oriented Programming", "Discrete Math", "Computer Architecture", "Cybersecurity Fundamentals", "Environmental Science"],
        ["Database Systems", "Operating Systems", "Computer Networks", "Cryptography", "Network Security", "Ethical Hacking"],
        ["Cyber Forensics", "Information Security Management", "Cloud Security", "Blockchain & Smart Contracts", "Incident Response", "Capstone Project"]
    ],
    "MECH": [
        ["Engineering Mechanics", "Engineering Math I", "Engineering Graphics", "Physics", "Communication Skills", "Engineering Workshop"],
        ["Thermodynamics", "Material Science", "Fluid Mechanics", "Strength of Materials", "Manufacturing Processes", "Environmental Science"],
        ["Kinematics of Machinery", "Heat Transfer", "Machine Design", "CAD/CAM", "Mechatronics", "Automobile Engineering"],
        ["Dynamics of Machinery", "Robotics", "Finite Element Analysis", "Power Plant Engineering", "Renewable Energy", "Capstone Project"]
    ],
    "CIVIL": [
        ["Engineering Mechanics", "Engineering Math I", "Engineering Graphics", "Physics", "Communication Skills", "Engineering Workshop"],
        ["Surveying", "Solid Mechanics", "Fluid Mechanics", "Building Materials", "Engineering Geology", "Environmental Science"],
        ["Structural Analysis I", "Geotechnical Engineering", "Environmental Engineering", "Transportation Engineering", "Concrete Technology", "Water Resources"],
        ["Structural Analysis II", "Construction Management", "Steel Structures", "Foundation Engineering", "Urban Planning", "Capstone Project"]
    ]
}

GENERIC_CURRICULUM_DATA: Dict[int, List[Tuple[str, str, int]]] = {
    1: [
        ("Sub_1_1", "Introduction to Programming & Problem Solving", 4),
        ("Sub_1_2", "Calculus & Analytical Geometry", 4),
        ("Sub_1_3", "Physics for Engineers", 3),
        ("Sub_1_4", "Engineering Chemistry", 3),
        ("Sub_1_5", "Basic Electrical & Electronics Engineering", 3),
        ("Sub_1_6", "Technical Communication & Soft Skills", 3),
        ("Sub_1_7", "Digital Logic & Circuit Design", 4),
        ("Sub_1_8", "Environmental Science & Sustainability", 3),
        ("Sub_1_9", "Engineering Workshop Practice", 3),
        ("Sub_1_10", "Discrete Mathematics", 4),
        ("Sub_1_11", "Principles of Economics & Management", 3),
        ("Sub_1_12", "Computer Organization & Hardware Lab", 4),
        ("Sub_1_13", "Python for Rapid Prototyping", 3),
        ("Sub_1_14", "Engineering Graphics & CAD", 3),
        ("Sub_1_15", "Ethics & Human Values in Computing", 3),
    ],
    2: [
        ("Sub_2_1", "Data Structures and Algorithms", 4),
        ("Sub_2_2", "Object-Oriented Programming with Java", 4),
        ("Sub_2_3", "Linear Algebra & Vector Spaces", 3),
        ("Sub_2_4", "Computer Architecture & Microprocessors", 4),
        ("Sub_2_5", "Probability and Applied Statistics", 3),
        ("Sub_2_6", "Web Development Fundamentals", 3),
        ("Sub_2_7", "Software Engineering Principles", 4),
        ("Sub_2_8", "Signals and Systems", 3),
        ("Sub_2_9", "Relational Database Concepts", 4),
        ("Sub_2_10", "Formal Languages & Automata Theory", 3),
        ("Sub_2_11", "User Interface Design Fundamentals", 3),
        ("Sub_2_12", "Digital Signal Processing", 3),
        ("Sub_2_13", "Linux System & Shell Scripting", 3),
        ("Sub_2_14", "Numerical Methods in Computing", 3),
        ("Sub_2_15", "Technical Seminar & Scientific Writing", 3),
    ],
    3: [
        ("Sub_3_1", "Database Management Systems & SQL", 4),
        ("Sub_3_2", "Operating Systems Architecture", 4),
        ("Sub_3_3", "Design & Analysis of Algorithms", 4),
        ("Sub_3_4", "Computer Networks & Protocols", 4),
        ("Sub_3_5", "Artificial Intelligence Principles", 4),
        ("Sub_3_6", "Full-Stack Web Development", 3),
        ("Sub_3_7", "Mobile Application Development", 3),
        ("Sub_3_8", "Cryptography & Network Security", 3),
        ("Sub_3_9", "Cloud Computing Foundations", 3),
        ("Sub_3_10", "Compiler Design & Construction", 3),
        ("Sub_3_11", "Data Warehousing and Mining", 3),
        ("Sub_3_12", "Distributed Systems Concepts", 3),
        ("Sub_3_13", "Cyber Forensics & Incident Response", 3),
        ("Sub_3_14", "Natural Language Processing Basics", 3),
        ("Sub_3_15", "Agile & DevOps Project Management", 3),
    ],
    4: [
        ("Sub_4_1", "Machine Learning Systems & Algorithms", 4),
        ("Sub_4_2", "Deep Learning & Neural Networks", 4),
        ("Sub_4_3", "Big Data Analytics & Streaming", 4),
        ("Sub_4_4", "DevOps & CI/CD Automation", 4),
        ("Sub_4_5", "Information Security & Applied Privacy", 4),
        ("Sub_4_6", "Internet of Things (IoT) & Smart Systems", 3),
        ("Sub_4_7", "Computer Vision & Image Processing", 3),
        ("Sub_4_8", "Blockchain Architecture & Smart Contracts", 3),
        ("Sub_4_9", "Cloud-Native Microservices", 3),
        ("Sub_4_10", "High-Performance Parallel Computing", 3),
        ("Sub_4_11", "Reinforcement Learning & Decision Making", 3),
        ("Sub_4_12", "Software Quality Assurance & Testing", 3),
        ("Sub_4_13", "Quantum Computing Foundations", 3),
        ("Sub_4_14", "Data Visualization & Business Intelligence", 3),
        ("Sub_4_15", "Applied Capstone Research Project", 3),
    ],
}


def build_curriculum_catalog() -> Dict[int, List[Tuple[str, str, int, str]]]:
    """Assembles complete multi-branch curriculum data incorporating robust PDF / fallback parser."""
    catalog: Dict[int, List[Tuple[str, str, int, str]]] = {1: [], 2: [], 3: [], 4: []}
    
    # 1. Add generic standard courses (CSE foundation)
    for sem in range(1, 5):
        for sid, sname, cred in GENERIC_CURRICULUM_DATA[sem]:
            catalog[sem].append((sid, sname, cred, "CSE"))

    # 2. Add real CSE curriculum via PDF parser / fallback
    cse_parsed = load_cse_curriculum()
    for sem in range(1, 5):
        if sem in cse_parsed:
            for sid, sname, cred, branch in cse_parsed[sem]:
                catalog[sem].append((sid, sname, cred, branch))

    # 3. Add other branch subjects
    for branch, sems_subjects in BRANCH_SUBJECTS_TEMPLATE.items():
        for sem in range(1, 5):
            subjects = sems_subjects[sem - 1]
            for i, subj_name in enumerate(subjects):
                subj_id = f"{branch}_Sub_{sem}_{i+1}"
                credits = assign_weighted_credits(subj_name)
                catalog[sem].append((subj_id, subj_name, credits, branch))

    return catalog


CURRICULUM_DATA = build_curriculum_catalog()

PREREQUISITE_RELATIONS: List[Tuple[str, str, str]] = [
    # Standard Curriculum Prerequisites
    ("Sub_2_1", "Sub_1_1", "HARD_PREREQ"),
    ("Sub_2_2", "Sub_1_1", "HARD_PREREQ"),
    ("Sub_2_3", "Sub_1_2", "HARD_PREREQ"),
    ("Sub_2_4", "Sub_1_7", "HARD_PREREQ"),
    ("Sub_2_5", "Sub_1_2", "HARD_PREREQ"),
    ("Sub_2_7", "Sub_1_1", "HARD_PREREQ"),
    ("Sub_2_9", "Sub_1_1", "HARD_PREREQ"),
    ("Sub_2_10", "Sub_1_10", "HARD_PREREQ"),
    ("Sub_2_13", "Sub_1_12", "HARD_PREREQ"),

    ("Sub_3_1", "Sub_2_9", "HARD_PREREQ"),
    ("Sub_3_2", "Sub_2_4", "HARD_PREREQ"),
    ("Sub_3_2", "Sub_2_13", "HARD_PREREQ"),
    ("Sub_3_3", "Sub_2_1", "HARD_PREREQ"),
    ("Sub_3_4", "Sub_3_2", "HARD_PREREQ"),
    ("Sub_3_5", "Sub_2_3", "HARD_PREREQ"),
    ("Sub_3_5", "Sub_2_5", "HARD_PREREQ"),
    ("Sub_3_6", "Sub_2_6", "HARD_PREREQ"),
    ("Sub_3_7", "Sub_2_2", "HARD_PREREQ"),
    ("Sub_3_8", "Sub_1_10", "HARD_PREREQ"),
    ("Sub_3_9", "Sub_2_4", "HARD_PREREQ"),
    ("Sub_3_10", "Sub_2_10", "HARD_PREREQ"),
    ("Sub_3_11", "Sub_2_9", "HARD_PREREQ"),
    ("Sub_3_12", "Sub_2_1", "HARD_PREREQ"),
    ("Sub_3_13", "Sub_2_13", "HARD_PREREQ"),
    ("Sub_3_14", "Sub_1_13", "HARD_PREREQ"),
    ("Sub_3_15", "Sub_2_7", "HARD_PREREQ"),

    ("Sub_4_1", "Sub_3_3", "HARD_PREREQ"),
    ("Sub_4_1", "Sub_3_5", "HARD_PREREQ"),
    ("Sub_4_2", "Sub_4_1", "HARD_PREREQ"),
    ("Sub_4_3", "Sub_3_1", "HARD_PREREQ"),
    ("Sub_4_3", "Sub_2_5", "HARD_PREREQ"),
    ("Sub_4_4", "Sub_3_15", "HARD_PREREQ"),
    ("Sub_4_4", "Sub_3_4", "HARD_PREREQ"),
    ("Sub_4_5", "Sub_3_8", "HARD_PREREQ"),
    ("Sub_4_6", "Sub_3_4", "HARD_PREREQ"),
    ("Sub_4_7", "Sub_3_5", "HARD_PREREQ"),
    ("Sub_4_7", "Sub_2_3", "HARD_PREREQ"),
    ("Sub_4_8", "Sub_3_8", "HARD_PREREQ"),
    ("Sub_4_8", "Sub_3_12", "HARD_PREREQ"),
    ("Sub_4_9", "Sub_3_9", "HARD_PREREQ"),
    ("Sub_4_9", "Sub_3_6", "HARD_PREREQ"),
    ("Sub_4_10", "Sub_3_2", "HARD_PREREQ"),
    ("Sub_4_11", "Sub_4_1", "HARD_PREREQ"),
    ("Sub_4_12", "Sub_2_7", "HARD_PREREQ"),
    ("Sub_4_13", "Sub_2_3", "HARD_PREREQ"),
    ("Sub_4_14", "Sub_3_11", "HARD_PREREQ"),
    ("Sub_4_15", "Sub_3_3", "HARD_PREREQ"),
    ("Sub_4_15", "Sub_3_1", "HARD_PREREQ"),

    ("Sub_1_12", "Sub_1_7", "COREQ"),
    ("Sub_3_6", "Sub_3_1", "COREQ"),
    ("Sub_4_6", "Sub_4_13", "ANTIREQ"),
    ("Sub_4_13", "Sub_4_6", "ANTIREQ"),

    # Explicit CSE Prerequisites extracted from curriculum
    ("22CS206", "22TP105", "HARD_PREREQ"),  # DAA requires PPS
    ("22CS206", "22MT107", "HARD_PREREQ"),  # DAA requires DMS
    ("22CS206", "22TP201", "HARD_PREREQ"),  # DAA requires DS
    ("22CS207", "22CS205", "HARD_PREREQ"),  # OS requires COA
    ("22CS207", "22CS202", "HARD_PREREQ"),  # OS requires DLD
    ("22CS201", "22MT107", "HARD_PREREQ"),  # DBMS requires DMS
]

for branch in BRANCH_SUBJECTS_TEMPLATE.keys():
    PREREQUISITE_RELATIONS.extend([
        (f"{branch}_Sub_2_1", f"{branch}_Sub_1_1", "HARD_PREREQ"),
        (f"{branch}_Sub_2_2", f"{branch}_Sub_1_2", "HARD_PREREQ"),
        (f"{branch}_Sub_3_1", f"{branch}_Sub_2_1", "HARD_PREREQ"),
        (f"{branch}_Sub_3_2", f"{branch}_Sub_2_2", "HARD_PREREQ"),
        (f"{branch}_Sub_4_1", f"{branch}_Sub_3_1", "HARD_PREREQ"),
        (f"{branch}_Sub_4_6", f"{branch}_Sub_3_6", "HARD_PREREQ"),
    ])

COURSE_EQUIVALENCES: List[Tuple[str, str, str]] = [
    ("Sub_3_6", "Sub_4_9", "ADVANCED_EQUIVALENT"),
    ("Sub_3_14", "Sub_4_2", "FOUNDATIONAL_TRACK"),
    ("Sub_3_9", "Sub_4_4", "INFRA_EQUIVALENT"),
    ("Sub_2_6", "Sub_3_6", "ELECTIVE_BRIDGE"),
    ("Sub_3_11", "Sub_4_3", "ANALYTICS_EQUIVALENT"),
]

ACADEMIC_POLICIES: List[Tuple[str, str, str, str, str, str]] = [
    (
        "POL_01",
        "Section 1.1",
        "Degree Completion & Graduation Thresholds",
        "Students must accumulate a minimum of 160 earned credit units across 8 academic semesters with a cumulative grade point average (CGPA) >= 5.0 to be eligible for the Bachelor of Technology degree conferral.",
        "Graduation",
        "[Policy §1.1: Degree Completion]"
    ),
    (
        "POL_02",
        "Section 2.1",
        "Credit Load & Overload Regulations",
        "The standard semester course registration workload is capped at 20 credit units. Exceptional students with a cumulative GPA >= 8.5 (Honors threshold) may request an academic overload up to 24 credits upon formal faculty approval.",
        "Enrollment",
        "[Policy §2.1: Credit Load & Overload]"
    ),
    (
        "POL_03",
        "Section 2.2",
        "Academic Probation & Minimum Term Load",
        "Students with a cumulative GPA below 6.0 are placed on academic warning/probation. In accordance with remedial guidelines, credit registration for probationary terms is restricted to a maximum of 16 credits.",
        "Academic Standing",
        "[Policy §2.2: Academic Probation]"
    ),
    (
        "POL_04",
        "Section 3.1",
        "Prerequisite Sequential Progression & Enforcement",
        "Enrollment in advanced courses strictly requires prior successful completion of all designated HARD_PREREQ dependencies. Co-requisites must be taken in the same semester or previously cleared.",
        "Prerequisites",
        "[Policy §3.1: Prerequisite Progression]"
    ),
    (
        "POL_05",
        "Section 3.2",
        "Prerequisite Waiver & Prior Learning Assessment",
        "A prerequisite waiver may be granted upon submission of verifiable prior learning credentials (e.g. MOOC certifications, transfer credits) subject to formal faculty petition review and department chair approval.",
        "Waivers",
        "[Policy §3.2: Prerequisite Waiver]"
    ),
    (
        "POL_06",
        "Section 4.1",
        "Course Substitution & Equivalency Mapping",
        "When required courses are unavailable or conflict with degree milestones, students may enroll in department-approved equivalent electives listed in the Course Equivalency Matrix.",
        "Equivalence",
        "[Policy §4.1: Course Substitution]"
    ),
    (
        "POL_07",
        "Section 5.1",
        "Anti-Requisite Mutual Exclusion Policy",
        "Courses designated as ANTIREQ share overlapping instructional syllabi and cannot both be counted towards cumulative degree graduation credits.",
        "Prerequisites",
        "[Policy §5.1: Anti-Requisites]"
    ),
    (
        "POL_08",
        "Section 6.1",
        "Capstone Research Project Eligibility Criteria",
        "Registration for Sub_4_15 (Applied Capstone Research Project) mandates standing in Semester 4 or above, satisfaction of Sub_3_3 and Sub_3_1 prerequisites, and no active probationary holds.",
        "Capstone",
        "[Policy §6.1: Capstone Eligibility]"
    ),
]


def delete_existing_db(db_path: Union[str, Path] = DB_PATH) -> None:
    """Deletes existing SQLite database file if present so new schema is cleanly generated."""
    target = Path(db_path)
    if target.exists():
        try:
            os.remove(target)
            print(f"[CLEANUP] Deleted existing database at {target}")
        except Exception as e:
            print(f"[WARN] Could not delete {target}: {e}")


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Creates the complete relational schema with 8 normalized tables."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Degree_Requirements (
            RequirementID INTEGER PRIMARY KEY AUTOINCREMENT,
            RuleKey TEXT UNIQUE NOT NULL,
            RuleValue TEXT NOT NULL,
            Description TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subjects (
            SubjectID TEXT PRIMARY KEY,
            SubjectName TEXT NOT NULL,
            Branch TEXT NOT NULL,
            Semester INTEGER NOT NULL CHECK(Semester BETWEEN 1 AND 4),
            Credits INTEGER NOT NULL CHECK(Credits BETWEEN 1 AND 10)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            RegNo       TEXT PRIMARY KEY,
            StudentName TEXT NOT NULL,
            Branch      TEXT NOT NULL,
            Semester    INTEGER NOT NULL CHECK(Semester BETWEEN 1 AND 8),
            CGPA        REAL    NOT NULL CHECK(CGPA BETWEEN 0.0 AND 10.0),
            Goal        TEXT    NOT NULL,
            TotalCredits INTEGER DEFAULT 0,
            YearOfJoin   TEXT    DEFAULT '',
            DeptCode     TEXT    DEFAULT '',
            Section      TEXT    DEFAULT '',
            Department   TEXT    DEFAULT ''
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student_Subjects (
            RegistrationID INTEGER PRIMARY KEY AUTOINCREMENT,
            RegNo TEXT NOT NULL,
            SubjectID TEXT NOT NULL,
            EnrollmentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (RegNo) REFERENCES Students(RegNo) ON DELETE CASCADE,
            FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID) ON DELETE CASCADE,
            UNIQUE(RegNo, SubjectID)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Prerequisites (
            PrereqID INTEGER PRIMARY KEY AUTOINCREMENT,
            SubjectID TEXT NOT NULL,
            PrereqSubjectID TEXT NOT NULL,
            PrereqType TEXT NOT NULL CHECK(PrereqType IN ('HARD_PREREQ', 'COREQ', 'ANTIREQ')),
            FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID) ON DELETE CASCADE,
            FOREIGN KEY (PrereqSubjectID) REFERENCES Subjects(SubjectID) ON DELETE CASCADE,
            UNIQUE(SubjectID, PrereqSubjectID, PrereqType)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Course_Equivalences (
            EquivalenceID INTEGER PRIMARY KEY AUTOINCREMENT,
            SubjectID TEXT NOT NULL,
            EquivalentSubjectID TEXT NOT NULL,
            EquivalenceType TEXT NOT NULL,
            FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID) ON DELETE CASCADE,
            FOREIGN KEY (EquivalentSubjectID) REFERENCES Subjects(SubjectID) ON DELETE CASCADE,
            UNIQUE(SubjectID, EquivalentSubjectID)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Academic_Policies (
            PolicyID TEXT PRIMARY KEY,
            Section TEXT NOT NULL,
            Title TEXT NOT NULL,
            Content TEXT NOT NULL,
            Category TEXT NOT NULL,
            CitationCode TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Faculty_Petitions (
            PetitionID TEXT PRIMARY KEY,
            RegNo TEXT NOT NULL,
            SubjectID TEXT NOT NULL,
            PetitionType TEXT NOT NULL CHECK(PetitionType IN ('PREREQUISITE_WAIVER', 'CREDIT_OVERLOAD', 'COURSE_SUBSTITUTION', 'SPECIAL_PERMISSION')),
            Reason TEXT NOT NULL,
            Status TEXT NOT NULL DEFAULT 'PENDING' CHECK(Status IN ('PENDING', 'APPROVED', 'REJECTED')),
            FacultyRemarks TEXT,
            Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            AuditHash TEXT NOT NULL,
            FOREIGN KEY (RegNo) REFERENCES Students(RegNo) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Waiver_Requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT NOT NULL,
            course_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            waiver_type TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            approver_id TEXT,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ALTER TABLE execution blocks to safely append missing columns if tables pre-exist
    cursor.execute("PRAGMA table_info(Students);")
    existing_student_cols = {row[1] for row in cursor.fetchall()}
    if "Branch" not in existing_student_cols:
        cursor.execute("ALTER TABLE Students ADD COLUMN Branch TEXT;")

    cursor.execute("PRAGMA table_info(Subjects);")
    existing_subject_cols = {row[1] for row in cursor.fetchall()}
    if "Branch" not in existing_subject_cols:
        cursor.execute("ALTER TABLE Subjects ADD COLUMN Branch TEXT;")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subjects_semester ON Subjects(Semester);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subjects_branch ON Subjects(Branch);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_semester ON Students(Semester);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_branch ON Students(Branch);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_subjects_regno ON Student_Subjects(RegNo);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_subjects_subjectid ON Student_Subjects(SubjectID);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_waivers_regno ON Waiver_Requests(reg_no);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prereq_subjectid ON Prerequisites(SubjectID);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prereq_prereqsubjectid ON Prerequisites(PrereqSubjectID);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_policies_category ON Academic_Policies(Category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_petitions_regno ON Faculty_Petitions(RegNo);")


def populate_degree_rules(cursor: sqlite3.Cursor) -> None:
    """Inserts degree requirements and catalog rules."""
    rules = [
        ("TOTAL_GRADUATION_CREDITS", "160", "Total credits required to graduate"),
        ("TOTAL_SEMESTERS", "8", "Total duration of undergraduate degree in semesters"),
        ("SUBJECTS_PER_SEMESTER", "6", "Mandatory subjects enrolled per semester"),
        ("SEMESTER_CREDIT_TARGET", "20", "Target average credits per semester (20 * 8 = 160 credits)"),
        ("MAX_CREDIT_LIMIT_STANDARD", "20", "Standard maximum credit load per semester"),
        ("MAX_CREDIT_LIMIT_OVERLOAD", "24", "Maximum allowed credit load with faculty overload approval"),
        ("MIN_PROBATION_CGPA", "6.0", "CGPA threshold below which student is on academic probation"),
        ("HONORS_CGPA_THRESHOLD", "8.5", "CGPA threshold for academic honors classification"),
        ("CURRICULUM_SEMESTERS_CONFIGURED", "4", "Number of catalog semesters populated in this phase"),
        ("SUBJECT_POOL_PER_SEMESTER", "15", "Available subjects in curriculum pool per semester"),
    ]
    cursor.executemany("""
        INSERT INTO Degree_Requirements (RuleKey, RuleValue, Description)
        VALUES (?, ?, ?);
    """, rules)


def populate_subjects(cursor: sqlite3.Cursor) -> int:
    """Inserts all subjects across branches and semesters."""
    all_subjects = []
    seen = set()
    for sem, subjects in CURRICULUM_DATA.items():
        for sid, sname, cred, branch in subjects:
            if sid not in seen:
                seen.add(sid)
                all_subjects.append((sid, sname, branch, sem, cred))

    cursor.executemany("""
        INSERT INTO Subjects (SubjectID, SubjectName, Branch, Semester, Credits)
        VALUES (?, ?, ?, ?, ?);
    """, all_subjects)
    return len(all_subjects)


def populate_prerequisites(cursor: sqlite3.Cursor) -> int:
    """Inserts all explicit prerequisite, corequisite, and antirequisite relations."""
    cursor.executemany("""
        INSERT INTO Prerequisites (SubjectID, PrereqSubjectID, PrereqType)
        VALUES (?, ?, ?);
    """, PREREQUISITE_RELATIONS)
    return len(PREREQUISITE_RELATIONS)


def populate_course_equivalences(cursor: sqlite3.Cursor) -> int:
    """Inserts course substitutions and equivalent elective tracks."""
    cursor.executemany("""
        INSERT INTO Course_Equivalences (SubjectID, EquivalentSubjectID, EquivalenceType)
        VALUES (?, ?, ?);
    """, COURSE_EQUIVALENCES)
    return len(COURSE_EQUIVALENCES)


def populate_academic_policies(cursor: sqlite3.Cursor) -> int:
    """Inserts policy records into Academic_Policies table for Graph-RAG retrieval."""
    cursor.executemany("""
        INSERT INTO Academic_Policies (PolicyID, Section, Title, Content, Category, CitationCode)
        VALUES (?, ?, ?, ?, ?, ?);
    """, ACADEMIC_POLICIES)
    return len(ACADEMIC_POLICIES)


def generate_unique_student_names(count: int = 50) -> List[str]:
    """Generates unique full names."""
    pairs = set()
    names = []
    while len(names) < count:
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        full = f"{fn} {ln}"
        if full not in pairs:
            pairs.add(full)
            names.append(full)
    return names


def populate_students(cursor: sqlite3.Cursor, count: int = 150) -> List[Dict[str, Any]]:
    """Inserts comprehensive, diverse student records across standard and Vignan registration formats."""
    full_names = generate_unique_student_names(count)
    students = []
    branches = ['CSE', 'AIML', 'CSCS', 'BBA', 'MECH', 'CIVIL']

    for i in range(count):
        branch = branches[i % len(branches)]
        # Half standard REG format, half Vignan 221FA04xxx / 231FA09xxx format
        if i < 60:
            reg_no = f"REG{1001 + i}"
            semester = (i % 4) + 1
        elif i < 90:
            reg_no = f"221FA04{str(i - 60 + 1).zfill(3)}"
            branch = "CSE"
            semester = (i % 2) + 3 # Sem 3 or 4
        elif i < 120:
            reg_no = f"231FA09{str(i - 90 + 1).zfill(3)}"
            branch = "AIML"
            semester = (i % 2) + 1 # Sem 1 or 2
        else:
            reg_no = f"211FA10{str(i - 120 + 1).zfill(3)}"
            branch = "CSCS"
            semester = 4

        name = full_names[i]
        goal = CAREER_GOALS[i % len(CAREER_GOALS)]

        base_gpa = random.gauss(7.85, 1.25)
        cgpa = max(4.20, min(9.95, round(base_gpa, 2)))

        students.append({
            "reg_no": reg_no,
            "name": name,
            "branch": branch,
            "semester": semester,
            "cgpa": cgpa,
            "goal": goal
        })

    cursor.executemany("""
        INSERT INTO Students (RegNo, StudentName, Branch, Semester, CGPA, Goal)
        VALUES (:reg_no, :name, :branch, :semester, :cgpa, :goal);
    """, students)

    return students



def enroll_students_in_subjects(cursor: sqlite3.Cursor, students: List[Dict[str, Any]]) -> int:
    """Enrolls each student in subjects from their assigned semester and branch."""
    enrollments = []
    for st in students:
        sem = st["semester"]
        branch = st["branch"]
        
        pool = [s for s in CURRICULUM_DATA[sem] if s[3] == branch]
        
        if len(pool) >= 6:
            chosen = random.sample(pool, 6)
        else:
            chosen = pool

        for subj_id, _, _, _ in chosen:
            enrollments.append((st["reg_no"], subj_id))

    cursor.executemany("""
        INSERT INTO Student_Subjects (RegNo, SubjectID)
        VALUES (?, ?);
    """, enrollments)

    return len(enrollments)


def populate_initial_faculty_petitions(cursor: sqlite3.Cursor) -> int:
    """Seeds sample faculty petitions with dynamic branch-assigned subject codes and cryptographic audit hashes."""
    def make_hash(reg_no: str, subj_id: str, ptype: str) -> str:
        raw = f"{reg_no}:{subj_id}:{ptype}:{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get_student_branch(reg_no: str, fallback: str = "CSE") -> str:
        cursor.execute("SELECT Branch FROM Students WHERE RegNo = ?;", (reg_no,))
        row = cursor.fetchone()
        return row[0] if (row and row[0]) else fallback

    branch_1001 = get_student_branch("REG1001", "CSE")
    branch_1004 = get_student_branch("REG1004", "CSCS")
    branch_1012 = get_student_branch("REG1012", "CIVIL")

    # Match subject based on dynamically queried branch
    subj_1001 = "Sub_4_2" if branch_1001 == "CSE" else f"{branch_1001}_Sub_4_2"
    subj_1004 = f"{branch_1004}_Sub_3_3" if branch_1004 != "CSE" else "Sub_3_3"
    subj_1012 = f"{branch_1012}_Sub_3_6" if branch_1012 != "CSE" else "Sub_3_6"

    petitions = [
        (
            "PET_8A1B",
            "REG1001",
            subj_1001,
            "PREREQUISITE_WAIVER",
            f"Completed DeepLearning.AI Specialization on Coursera with verified credential. Requesting waiver for Sub_4_1 prerequisite.",
            "PENDING",
            None,
            make_hash("REG1001", subj_1001, "PREREQUISITE_WAIVER")
        ),
        (
            "PET_4C2D",
            "REG1004",
            subj_1004,
            "CREDIT_OVERLOAD",
            "Student holds 9.1 CGPA in Honors track. Requesting 24 credit overload for Semester 3 accelerated graduation pathway.",
            "APPROVED",
            "Approved by Department Chair Prof. K. Rao. Student meets GPA >= 8.5 threshold [Policy §2.1].",
            make_hash("REG1004", subj_1004, "CREDIT_OVERLOAD")
        ),
        (
            "PET_9E3F",
            "REG1012",
            subj_1012,
            "COURSE_SUBSTITUTION",
            f"Course schedule conflict between {subj_1012} and {branch_1012}_Sub_3_2. Requesting enrollment in approved substitute Sub_4_9 [Policy §4.1].",
            "PENDING",
            None,
            make_hash("REG1012", subj_1012, "COURSE_SUBSTITUTION")
        )
    ]

    cursor.executemany("""
        INSERT INTO Faculty_Petitions (PetitionID, RegNo, SubjectID, PetitionType, Reason, Status, FacultyRemarks, AuditHash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, petitions)

    return len(petitions)


def run_verification_queries(conn: sqlite3.Connection) -> None:
    """Runs database verification audits."""
    cursor = conn.cursor()
    print("\n" + "=" * 70)
    print(" UNIVERSITY DATABASE INTEGRITY AUDIT")
    print("=" * 70)

    tables = [
        "Degree_Requirements", "Subjects", "Students", "Student_Subjects",
        "Prerequisites", "Course_Equivalences", "Academic_Policies", "Faculty_Petitions", "Waiver_Requests"
    ]

    counts = {}
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        counts[tbl] = cursor.fetchone()[0]

    print("\n>>> 1. Aggregate Data Counts:")
    for tbl, cnt in counts.items():
        print(f"  * {tbl:25} : {cnt} records")

    cursor.execute("""
        SELECT RegNo, COUNT(SubjectID) as SubCount
        FROM Student_Subjects
        GROUP BY RegNo
        HAVING SubCount < 6;
    """)
    violations = cursor.fetchall()
    if not violations:
        print("\n>>> 2. Constraint Check (Enrollment Rule):")
        print("  [SUCCESS] All students are enrolled in at least 6 subjects!")
    else:
        print(f"  [FAILURE] Rule violated for {len(violations)} students: {violations}")

    cursor.execute("""
        SELECT PrereqType, COUNT(*) FROM Prerequisites GROUP BY PrereqType;
    """)
    print("\n>>> 3. Prerequisite Graph Edges by Type:")
    for ptype, count in cursor.fetchall():
        print(f"  * {ptype:15} : {count} directed edges")

    cursor.execute("""
        SELECT RegNo, StudentName, Branch, Semester, CGPA, Goal FROM Students LIMIT 5;
    """)
    print("\n>>> 4. Sample Students with Branch & Standing:")
    for r in cursor.fetchall():
        print(f"  * {r[0]} - {r[1]} | Branch: {r[2]} | Sem: {r[3]} | CGPA: {r[4]:.2f} | Goal: {r[5]}")

    cursor.execute("""
        SELECT PetitionID, RegNo, SubjectID, PetitionType FROM Faculty_Petitions;
    """)
    print("\n>>> 5. Sample Faculty Petitions (Dynamic Branch Subjects):")
    for r in cursor.fetchall():
        print(f"  * {r[0]} | Student: {r[1]} | Subject: {r[2]} | Type: {r[3]}")

    print("\nDatabase initialization and verification completed successfully.\n")


def init_university_database(db_path: Union[str, Path] = DB_PATH, seed: int = 42) -> sqlite3.Connection:
    """Main orchestration function to initialize and populate the SQLite database."""
    if seed is not None:
        random.seed(seed)

    target_path = Path(db_path)
    print(f"Starting University Database Initialization...")
    print(f"Target Database File: {target_path}")

    # Force a clean database slate
    delete_existing_db(target_path)

    conn = sqlite3.connect(str(target_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        create_schema(cursor)
        print("[SCHEMA] Created all relational tables.")

        populate_degree_rules(cursor)
        subj_count = populate_subjects(cursor)
        prereq_count = populate_prerequisites(cursor)
        equiv_count = populate_course_equivalences(cursor)
        policy_count = populate_academic_policies(cursor)
        print(f"[POPULATE] Inserted {subj_count} subjects, {prereq_count} prereq edges, {equiv_count} equivalences, {policy_count} policies.")

        students = populate_students(cursor, count=60)
        enrollment_count = enroll_students_in_subjects(cursor, students)
        petition_count = populate_initial_faculty_petitions(cursor)
        print(f"[POPULATE] Inserted {len(students)} students, {enrollment_count} enrollments, {petition_count} faculty petitions.")

        conn.commit()
        print("[COMMIT] All database transactions committed successfully.")

        run_verification_queries(conn)
        return conn

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    conn = init_university_database()
    conn.close()