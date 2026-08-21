"""
University Academic Advising & Curriculum Database Initializer
=============================================================
A complete, standalone Python script using sqlite3 and random libraries
to create, format, and populate a local SQLite database (university.db).

Requirements:
1. University Curriculum Rules:
   - 160 total credits required to graduate over 8 semesters (~20 credits/semester).
   - 4 Semesters (Semesters 1 through 4).
   - 15 subjects per semester pool (60 subjects total: Sub_1_1 to Sub_4_15).
   - 3 or 4 credits per subject (expected 20 credits per 6-subject semester).

2. Student Database Schema & Logic:
   - RegNo (Primary Key, e.g., REG1001 to REG1050)
   - StudentName (Realistic randomly generated names)
   - Semester (Random between 1 and 4)
   - CGPA (Random float between 5.0 and 10.0, rounded to 2 decimals)
   - Goal (Random tech career goals)

3. Subject Registration Constraints (The 6-Subject Rule):
   - Student_Subjects mapping table (RegNo, SubjectID) with Foreign Keys.
   - Enforces exactly 6 subjects randomly enrolled from the student's current semester pool.

4. Mock Data Generation:
   - 50 Students.
   - 60 Subjects.
   - 300 Student-Subject enrollments (50 students * 6 subjects).

5. Clean Run & Console Verification:
   - Drops/deletes previous university.db if existing.
   - Executes validation queries and prints sample student profiles with enrolled subjects.
"""

import os
import random
import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Determine DB file location (stored in the same directory as this script or backend/)
SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "university.db"

# ---------------------------------------------------------------------------
# Curriculum Catalog & Career Goals Definition
# ---------------------------------------------------------------------------

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

# 15 Subjects for each of the 4 Semesters (Total 60 subjects)
# Each semester has 5 subjects of 4 credits and 10 subjects of 3 credits
# (Pool average = 50 credits / 15 subjects = 3.333 cr/subj -> 6 subjects = 20 cr/semester)
CURRICULUM_DATA: Dict[int, List[Tuple[str, str, int]]] = {
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


def delete_existing_db(db_path: Path) -> None:
    """Deletes existing SQLite database file to ensure a clean run."""
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"[CLEANUP] Deleted existing database at: {db_path}")
        except Exception as e:
            print(f"[WARN] Failed to delete existing database file: {e}")


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Creates tables for Academic Rules, Subjects, Students, and Registrations."""
    # 1. Degree Requirements & University Curriculum Metadata Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Degree_Requirements (
            RuleKey TEXT PRIMARY KEY,
            RuleValue TEXT NOT NULL,
            Description TEXT
        );
    """)

    # 2. Subjects Table (The Catalog)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subjects (
            SubjectID TEXT PRIMARY KEY,
            SubjectName TEXT NOT NULL,
            Semester INTEGER NOT NULL CHECK(Semester BETWEEN 1 AND 4),
            Credits INTEGER NOT NULL CHECK(Credits IN (3, 4))
        );
    """)

    # 3. Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            RegNo TEXT PRIMARY KEY,
            StudentName TEXT NOT NULL,
            Semester INTEGER NOT NULL CHECK(Semester BETWEEN 1 AND 4),
            CGPA REAL NOT NULL CHECK(CGPA BETWEEN 0.0 AND 10.0),
            Goal TEXT NOT NULL
        );
    """)

    # 4. Student Subjects Relational Mapping Table (6-Subject Rule)
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

    # 5. Faculty Waiver Requests Table
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

    # Create Indexes for fast lookup
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subjects_semester ON Subjects(Semester);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_semester ON Students(Semester);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_subjects_regno ON Student_Subjects(RegNo);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_subjects_subjectid ON Student_Subjects(SubjectID);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_waivers_regno ON Waiver_Requests(reg_no);")



def populate_degree_rules(cursor: sqlite3.Cursor) -> None:
    """Inserts degree requirements and catalog rules."""
    rules = [
        ("TOTAL_GRADUATION_CREDITS", "160", "Total credits required to graduate"),
        ("TOTAL_SEMESTERS", "8", "Total duration of undergraduate degree in semesters"),
        ("SUBJECTS_PER_SEMESTER", "6", "Mandatory subjects enrolled per semester"),
        ("SEMESTER_CREDIT_TARGET", "20", "Target average credits per semester (20 * 8 = 160 credits)"),
        ("CURRICULUM_SEMESTERS_CONFIGURED", "4", "Number of catalog semesters populated in this phase"),
        ("SUBJECT_POOL_PER_SEMESTER", "15", "Available subjects in curriculum pool per semester"),
    ]
    cursor.executemany("""
        INSERT INTO Degree_Requirements (RuleKey, RuleValue, Description)
        VALUES (?, ?, ?);
    """, rules)


def populate_subjects(cursor: sqlite3.Cursor) -> int:
    """Populates 15 subjects for each of the 4 semesters (60 total subjects)."""
    subject_records: List[Tuple[str, str, int, int]] = []
    for semester, subjects in CURRICULUM_DATA.items():
        for subject_id, name, credits in subjects:
            subject_records.append((subject_id, name, semester, credits))

    cursor.executemany("""
        INSERT INTO Subjects (SubjectID, SubjectName, Semester, Credits)
        VALUES (?, ?, ?, ?);
    """, subject_records)
    return len(subject_records)


def populate_students(cursor: sqlite3.Cursor, count: int = 50) -> List[Tuple[str, str, int, float, str]]:
    """Populates 50 student records with realistic names, semester, CGPA, and career goals."""
    students: List[Tuple[str, str, int, float, str]] = []
    used_names = set()

    for i in range(1, count + 1):
        reg_no = f"REG{1000 + i}"

        # Generate realistic student name
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            if name not in used_names or len(used_names) >= (len(FIRST_NAMES) * len(LAST_NAMES)):
                used_names.add(name)
                break

        semester = random.randint(1, 4)
        cgpa = round(random.uniform(5.00, 10.00), 2)
        goal = random.choice(CAREER_GOALS)

        students.append((reg_no, name, semester, cgpa, goal))

    cursor.executemany("""
        INSERT INTO Students (RegNo, StudentName, Semester, CGPA, Goal)
        VALUES (?, ?, ?, ?, ?);
    """, students)
    return students


def enroll_students_in_subjects(cursor: sqlite3.Cursor, students: List[Tuple[str, str, int, float, str]]) -> int:
    """
    Enforces the 6-Subject Rule:
    For every student, randomly picks exactly 6 subjects out of the 15 available
    for their specific current semester.
    """
    # Fetch all subjects grouped by semester
    cursor.execute("SELECT SubjectID, Semester FROM Subjects;")
    all_subjects = cursor.fetchall()
    
    semester_subject_map: Dict[int, List[str]] = {1: [], 2: [], 3: [], 4: []}
    for sub_id, sem in all_subjects:
        if sem in semester_subject_map:
            semester_subject_map[sem].append(sub_id)

    registration_records: List[Tuple[str, str]] = []
    for reg_no, name, sem, cgpa, goal in students:
        available_subjects = semester_subject_map[sem]
        # Strictly pick exactly 6 subjects out of 15 available for current semester
        chosen_subjects = random.sample(available_subjects, 6)
        for sub_id in chosen_subjects:
            registration_records.append((reg_no, sub_id))

    cursor.executemany("""
        INSERT INTO Student_Subjects (RegNo, SubjectID)
        VALUES (?, ?);
    """, registration_records)
    return len(registration_records)


def run_verification_queries(conn: sqlite3.Connection) -> None:
    """Runs verification queries and formats the results for inspection."""
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("                      DATABASE VERIFICATION REPORT")
    print("=" * 80)

    # 1. Degree Requirements Summary
    print("\n>>> 1. Degree Requirements & Catalog Configuration:")
    cursor.execute("SELECT RuleKey, RuleValue, Description FROM Degree_Requirements;")
    for key, val, desc in cursor.fetchall():
        print(f"  * {key:30} : {val:5} ({desc})")

    # 2. Table Counts
    cursor.execute("SELECT COUNT(*) FROM Students;")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Subjects;")
    subject_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Student_Subjects;")
    registration_count = cursor.fetchone()[0]

    print("\n>>> 2. Aggregate Data Counts:")
    print(f"  * Total Students Generated     : {student_count} (Expected: 50)")
    print(f"  * Total Subjects in Catalog    : {subject_count} (Expected: 60 - 15/sem across 4 sems)")
    print(f"  * Total Subject Registrations  : {registration_count} (Expected: 300 - 50 students * 6 subjects)")

    # 3. 6-Subject Rule Verification
    cursor.execute("""
        SELECT RegNo, COUNT(SubjectID) as SubCount
        FROM Student_Subjects
        GROUP BY RegNo
        HAVING SubCount != 6;
    """)
    violations = cursor.fetchall()
    if not violations:
        print("\n>>> 3. Constraint Check (6-Subject Rule):")
        print("  [SUCCESS] All 50 students are enrolled in EXACTLY 6 subjects!")
    else:
        print(f"  [FAILURE] Rule violated for {len(violations)} students: {violations}")

    # 4. Semester Matching Verification
    cursor.execute("""
        SELECT COUNT(*)
        FROM Student_Subjects ss
        JOIN Students st ON ss.RegNo = st.RegNo
        JOIN Subjects sub ON ss.SubjectID = sub.SubjectID
        WHERE st.Semester != sub.Semester;
    """)
    mismatches = cursor.fetchone()[0]
    if mismatches == 0:
        print("  [SUCCESS] All enrolled subjects strictly match the student's current semester!")
    else:
        print(f"  [FAILURE] {mismatches} subject enrollments have semester mismatches!")

    # 5. Sample Student Profiles & Their 6 Registered Subjects
    print("\n>>> 4. Detailed Sample Inspection (Displaying 3 Students):")
    print("-" * 80)

    cursor.execute("SELECT RegNo, StudentName, Semester, CGPA, Goal FROM Students ORDER BY RANDOM() LIMIT 3;")
    sample_students = cursor.fetchall()

    for idx, (reg_no, name, sem, cgpa, goal) in enumerate(sample_students, 1):
        print(f"\nStudent #{idx}: {name} ({reg_no})")
        print(f"  * Current Semester : Semester {sem}")
        print(f"  * Cumulative GPA   : {cgpa:.2f} / 10.00")
        print(f"  * Career Goal      : {goal}")
        print("  * Enrolled Subjects (6-Subject Registration):")

        cursor.execute("""
            SELECT sub.SubjectID, sub.SubjectName, sub.Credits
            FROM Student_Subjects ss
            JOIN Subjects sub ON ss.SubjectID = sub.SubjectID
            WHERE ss.RegNo = ?
            ORDER BY LENGTH(sub.SubjectID), sub.SubjectID;
        """, (reg_no,))
        enrolled_subjects = cursor.fetchall()

        total_credits = 0
        for sub_id, sub_name, credits in enrolled_subjects:
            print(f"    - [{sub_id}] {sub_name:<48} | {credits} Credits")
            total_credits += credits

        print(f"    -> Total Semester Credits Enrolled: {total_credits} Credits")
        print("-" * 80)

    print("\nDatabase initialization and verification completed successfully.\n")


def init_university_database(db_path: Path = DB_PATH, seed: int = None) -> sqlite3.Connection:
    """
    Main orchestration function to initialize and populate the SQLite database.
    """
    if seed is not None:
        random.seed(seed)

    print(f"Starting University Database Initialization...")
    print(f"Target Database File: {db_path}")

    # 1. Clean old database
    delete_existing_db(db_path)

    # 2. Connect and enable Foreign Key constraints
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # 3. Create Schema
        create_schema(cursor)
        print("[SCHEMA] Created tables: Degree_Requirements, Subjects, Students, Student_Subjects.")

        # 4. Populate Catalog & Rules
        populate_degree_rules(cursor)
        subj_count = populate_subjects(cursor)
        print(f"[POPULATE] Inserted {subj_count} subjects across 4 semesters (15 per semester).")

        # 5. Populate Students
        students = populate_students(cursor, count=50)
        print(f"[POPULATE] Inserted {len(students)} student records with random CGPA, Semesters, and Goals.")

        # 6. Map Students to 6 Subjects
        enrollment_count = enroll_students_in_subjects(cursor, students)
        print(f"[POPULATE] Inserted {enrollment_count} student-subject enrollments (6 subjects per student).")

        # Commit transactions
        conn.commit()
        print("[COMMIT] All transactions committed successfully.")

        # 7. Verification Queries
        run_verification_queries(conn)
        return conn

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Database initialization failed: {e}")
        raise
    finally:
        pass


if __name__ == "__main__":
    conn = init_university_database()
    conn.close()
