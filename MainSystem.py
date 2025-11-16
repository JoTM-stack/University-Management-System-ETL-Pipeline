import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
import string
from datetime import time, date, timedelta

fake = Faker()

# ==========================
# DB CONNECTION
# ==========================
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            database="university_system",
            port=3306
        )
        if conn.is_connected():
            print("Connected to university_system")
        return conn
    except Error as e:
        print("DB Connection error:", e)
        return None

# ==========================
# UTILS
# ==========================
def generate_unique_student_number(existing):
    while True:
        num = "STU" + ''.join(random.choices(string.digits, k=6))
        if num not in existing:
            existing.add(num)
            return num

# ==========================
# INSERT LOOKUP DATA
# ==========================
def insert_base_data(cursor):

    # qualifications
    cursor.executemany("""
        INSERT IGNORE INTO qualifications (qualification_name)
        VALUES (%s)
    """, [
        ("Diploma in Computer Engineering",),
        ("Advanced Diploma in Computer Engineering",),
        ("Diploma in IT",),
        ("Diploma in Electrical Engineering",)
    ])

    # levels
    cursor.executemany("""
        INSERT IGNORE INTO levels (level_name)
        VALUES (%s)
    """, [("First Year",), ("Second Year",), ("Third Year",), ("Final Year",)])

    # departments
    cursor.executemany("""
        INSERT IGNORE INTO departments (department_name)
        VALUES (%s)
    """, [
        ("Computer Engineering",),
        ("Information Technology",),
        ("Electrical Engineering",),
        ("Mechanical Engineering",),
        ("AI & Robotics",)
    ])

    # staff roles
    cursor.executemany("""
        INSERT IGNORE INTO staff_roles (role_name)
        VALUES (%s)
    """, [
        ("Lecturer",),
        ("Technician",),
        ("Security",),
        ("Driver",),
        ("Admin",)
    ])

    print("Base lookup data inserted.")

# ==========================
# INSERT 1000 STAFF + COURSES + MODULES
# ==========================
def insert_staff_courses_modules(cursor):

    # ==========================
    # FETCH department + role IDs
    # ==========================
    cursor.execute("SELECT department_id, department_name FROM departments")
    dep_map = {name: d_id for (d_id, name) in cursor.fetchall()}

    cursor.execute("SELECT role_id, role_name FROM staff_roles")
    role_map = {name: r_id for (r_id, name) in cursor.fetchall()}

    print("Department Mapping:", dep_map)
    print("Role Mapping:", role_map)

    # ==========================
    # INSERT STAFF (SAFE)
    # ==========================
    staff = [
        ("Thandi", "Mokoena", "thandi@cput.ac.za", "0721112222", dep_map["Computer Engineering"], role_map["Lecturer"]),
        ("Jason", "Van Wyk", "jason@cput.ac.za", "0732223333", dep_map["Information Technology"], role_map["Lecturer"]),
        ("Peter", "Moyo", "p.moyo@cput.ac.za", "0713334444", dep_map["Computer Engineering"], role_map["Driver"]),
    ]

    cursor.executemany("""
        INSERT IGNORE INTO staff (first_name, last_name, email, phone, department_id, role_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, staff)

    # ==========================
    # INSERT COURSES (SAFE)
    # ==========================
    courses = [
        ("Introduction to Programming", dep_map["Information Technology"]),
        ("Network Fundamentals", dep_map["Information Technology"]),
        ("Embedded Systems", dep_map["Computer Engineering"]),
        ("Power Systems", dep_map["Electrical Engineering"])
    ]

    cursor.executemany("""
        INSERT IGNORE INTO courses (course_name, department_id)
        VALUES (%s, %s)
    """, courses)

    print("Staff, courses, and modules inserted safely.")

# ==========================
# INSERT 5000 STUDENTS + ENROLLMENTS + MARKS
# ==========================
def insert_students_data(cursor):
    existing = set()
    genders = ["Male", "Female", "Other"]

    # ---------------------------
    # INSERT 5000 STUDENTS
    # ---------------------------
    students = []
    for _ in range(5000):
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=30)

        students.append((
            generate_unique_student_number(existing),
            fake.first_name(),
            fake.last_name(),
            random.choice(genders),
            birthdate,
            random.randint(1, 4),  # level_id
            random.randint(1, 6),  # course_id (your DB has more now)
            random.randint(1, 5),  # department_id
            fake.email(),
            fake.phone_number()
        ))

    cursor.executemany("""
        INSERT IGNORE INTO students (
            student_number, first_name, last_name,
            gender, birthdate,
            level_id, course_id, department_id,
            email, phone
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, students)

    print("5000 Students inserted.")

    # Fetch inserted student IDs
    cursor.execute("SELECT student_id FROM students")
    student_ids = [x[0] for x in cursor.fetchall()]

    # Fetch modules
    cursor.execute("SELECT module_id FROM modules")
    module_ids = [x[0] for x in cursor.fetchall()]

    # Fetch qualifications
    cursor.execute("SELECT qualification_id FROM qualifications")
    qualification_ids = [x[0] for x in cursor.fetchall()]

    # ---------------------------
    # INSERT ENROLLMENTS (correct fields!)
    # ---------------------------
    enrollments = []
    for sid in student_ids:
        # assign 4 random modules per student
        selected = random.sample(module_ids, 4)

        for mid in selected:
            enrollments.append((
                sid,
                None,                # course_id – lookup later
                mid,
                2025,                # academic_year
                random.randint(1, 4),      # level_id
                random.choice(qualification_ids),
                "Active",
                fake.date_between(start_date="-1y", end_date="today"),
                random.randint(10, 30)      # credits
            ))

    cursor.executemany("""
        INSERT INTO student_enrollment (
            student_id, course_id, module_id,
            academic_year, level_id, qualification_id,
            status, enrollment_date, credits
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, enrollments)

    print(f"{len(enrollments)} student enrollments inserted.")

    # ---------------------------
    # INSERT MARKS
    # ---------------------------
    marks = []
    for sid in student_ids:
        selected = random.sample(module_ids, 4)
        for mid in selected:
            test = random.uniform(30, 100)
            exam = random.uniform(30, 100)
            avg = round((test + exam) / 2, 2)
            marks.append((sid, mid, test, exam, avg))

    cursor.executemany("""
            INSERT INTO student_marks (
                student_id, module_id,
                test_score, exam_score, final_score
            )
            VALUES (%s,%s,%s,%s,%s)
        """, marks)

    print(f"{len(marks)} marks inserted.")


# ==========================
# SHUTTLE SYSTEM
# ==========================
def insert_shuttle_data(cursor):

    # Insert shuttle points
    cursor.executemany("""
        INSERT IGNORE INTO shuttle_points (point_name, location)
        VALUES (%s, %s)
    """, [
        ("CPUT Bellville", "Symphony Way"),
        ("CPUT District Six", "Campus Entrance"),
    ])

    # Generate 20 bus entries
    buses = []
    for i in range(1, 21):  # 1 to 20
        bus_number = f"CPUT-B{i:03d}"  # formats 1 -> 001, 2 -> 002, etc.
        capacity = 40  # you can change this or make it random
        buses.append((bus_number, capacity))

    # Insert buses
    cursor.executemany("""
        INSERT IGNORE INTO buses (bus_number, capacity)
        VALUES (%s, %s)
    """, buses)

    print("Shuttle points & buses inserted.")

# ==========================
# APPLICANT SYSTEM
# ==========================
def insert_applicant_data(cursor):

    applicants = []
    for _ in range(200):
        matric = round(random.uniform(45, 95), 2)
        applicants.append((
            f"APP{random.randint(1000,9999)}",
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            random.randint(17, 30),
            matric,
            random.choice(["IT", "Engineering", "AI", "Mechanical"])
        ))

    cursor.executemany("""
        INSERT IGNORE INTO applicant_status (student_id, application_status, application_date)
        VALUES (NULL, %s, CURDATE())
    """, [])

    print("Applicants inserted.")

# ==========================
# BUS ALLOCATIONS
# ==========================
def insert_bus_allocations(cursor):

    # Get shuttle points (you already inserted 2)
    cursor.execute("SELECT point_id FROM shuttle_points")
    shuttle_points = [row[0] for row in cursor.fetchall()]

    # Get all buses (1–20)
    cursor.execute("SELECT bus_id FROM buses")
    buses = [row[0] for row in cursor.fetchall()]

    allocations = []

    # Assign each bus to each shuttle point
    for bus_id in buses:
        for point_id in shuttle_points:
            allocation_time = time(hour=(8 + point_id) % 24)  # example 08:00 & 09:00
            allocations.append((bus_id, point_id, allocation_time))

    cursor.executemany("""
        INSERT IGNORE INTO bus_allocations (bus_id, point_id, allocation_time)
        VALUES (%s, %s, %s)
    """, allocations)

    print("Bus allocations inserted.")

# ==========================
# COURSES AND DEPARTMENTS
# ==========================
def insert_courses_and_departments(cursor):

    # Insert departments
    departments = [
        ("Computer Science", "CS Building"),
        ("Electrical Engineering", "Engineering Block A"),
        ("Business & Management", "Business Block"),
        ("Applied Sciences", "Science Building"),
        ("Health Sciences", "Health Faculty"),
        ("Creative & Media Studies", "Creative Arts Block")
    ]

    cursor.executemany("""
        INSERT IGNORE INTO departments (department_id, department_name)
        VALUES (%s, %s)
    """, departments)

    # Fetch department IDs
    cursor.execute("SELECT department_id, department_name FROM departments")
    dept_dict = {name: d_id for (d_id, name) in cursor.fetchall()}

    # Insert courses
    courses = [
        # Information Technology (CS courses go here)
        ("Introduction to Programming", dept_dict["Information Technology"]),
        ("Data Structures & Algorithms", dept_dict["Information Technology"]),
        ("Database Systems", dept_dict["Information Technology"]),
        ("Operating Systems", dept_dict["Information Technology"]),
        ("Artificial Intelligence", dept_dict["AI & Robotics"]),
        ("Mobile Application Development", dept_dict["Information Technology"]),

        # Electrical Engineering
        ("Circuit Theory", dept_dict["Electrical Engineering"]),
        ("Signals & Systems", dept_dict["Electrical Engineering"]),
        ("Power Electronics", dept_dict["Electrical Engineering"]),
        ("Digital Logic Design", dept_dict["Electrical Engineering"]),
        ("Microcontrollers & Embedded Systems", dept_dict["Electrical Engineering"]),
        ("Renewable Energy Systems", dept_dict["Electrical Engineering"]),

        # Computer Engineering (instead of Business)
        ("Project Management", dept_dict["Computer Engineering"]),
        ("Digital Systems", dept_dict["Computer Engineering"]),
        ("Control Systems", dept_dict["Computer Engineering"]),

        # Mechanical Engineering (instead of Applied Sciences)
        ("Applied Physics", dept_dict["Mechanical Engineering"]),
        ("Mathematics for Sciences", dept_dict["Mechanical Engineering"]),
        ("Statistics & Probability", dept_dict["Mechanical Engineering"]),

        # AI & Robotics (instead of Creative Media)
        ("Robotics Fundamentals", dept_dict["AI & Robotics"]),
        ("Machine Learning", dept_dict["AI & Robotics"]),
        ("Computer Vision", dept_dict["AI & Robotics"]),
    ]


    cursor.executemany("""
        INSERT IGNORE INTO courses (course_name, department_id)
        VALUES (%s, %s)
    """, courses)

    print("Departments & 36 Courses inserted successfully.")

    # ==========================
    # LECTURER AND MODULE BY DEPARTMENTS
    # ==========================

def insert_lecturer_module_assignments(cursor):

    # 1️⃣ Get lecturers from correct table "staff_roles"
    cursor.execute("""
        SELECT staff_id 
        FROM staff 
        WHERE role_id IN (SELECT role_id FROM staff_roles WHERE role_name='Lecturer')
    """)
    lecturers = [row[0] for row in cursor.fetchall()]

    # 2️⃣ Fetch modules (must exist)
    cursor.execute("SELECT module_id FROM modules")
    modules = [row[0] for row in cursor.fetchall()]

    print("Lecturers:", len(lecturers))
    print("Modules:", len(modules))

    if len(lecturers) == 0:
        print("ERROR: No lecturers found. Skipping assignment.")
        return

    if len(modules) == 0:
        print("ERROR: No modules found. Skipping assignment.")
        return

    # 3️⃣ Assign lecturers to modules in round-robin
    assignments = []
    for i, lecturer in enumerate(lecturers):
        module_id = modules[i % len(modules)]
        assignments.append((lecturer, module_id))

    cursor.executemany("""
        INSERT INTO lecturer_module_assignment (staff_id, module_id)
        VALUES (%s, %s)
    """, assignments)

    print(f"{len(assignments)} lecturer-module assignments inserted.")

# INSERT MODULES

def insert_modules(cursor):

    # Fetch all course IDs
    cursor.execute("SELECT course_id FROM courses")
    course_ids = [row[0] for row in cursor.fetchall()]

    # Fetch all level IDs
    cursor.execute("SELECT level_id FROM levels")
    level_ids = [row[0] for row in cursor.fetchall()]

    modules = []
    for c_id in course_ids:
        for level in level_ids:
            module_name = f"Module {random.randint(100,999)} for Course {c_id}"
            modules.append((module_name, c_id, level))

    cursor.executemany("""
        INSERT IGNORE INTO modules (module_name, course_id, level_id)
        VALUES (%s, %s, %s)
    """, modules)

    print(f"{len(modules)} modules inserted.")

def insert_levels(cursor):
    levels = [
        ("Level 1",),
        ("Level 2",),
        ("Level 3",),
        ("Level 4",)
    ]

    cursor.executemany("INSERT INTO levels (level_name) VALUES (%s)", levels)
    print("Levels inserted.")

def insert_qualifications(cursor):
    qualifications = [
        ("Diploma in Engineering",),
        ("Bachelor of Technology",),
        ("Advanced Diploma",),
        ("Bachelor of Science",),
        ("Higher Certificate",),
        ("Postgraduate Diploma",)
    ]

    cursor.executemany("INSERT INTO qualifications (qualification_name) VALUES (%s)", qualifications)
    print("Qualifications inserted.")


# STUDENT ENROLLMENTS

def insert_student_enrollments(cursor):
    print("Inserting student enrollments...")

    # Fetch students
    cursor.execute("SELECT student_id FROM students")
    students = [row[0] for row in cursor.fetchall()]

    # Fetch courses
    cursor.execute("SELECT course_id FROM courses")
    courses = [row[0] for row in cursor.fetchall()]

    # Fetch modules
    cursor.execute("SELECT module_id, course_id FROM modules")
    modules = cursor.fetchall()  # (module_id, course_id)

    # Fetch levels
    cursor.execute("SELECT level_id FROM levels")
    levels = [row[0] for row in cursor.fetchall()]

    # Fetch qualifications
    cursor.execute("SELECT qualification_id FROM qualifications")
    qualifications = [row[0] for row in cursor.fetchall()]

    if not students or not courses or not modules or not levels or not qualifications:
        print("ERROR: Missing lookup data. Enrollment skipped.")
        return

    enrollments = []
    statuses = ["Active", "Completed", "Dropped"]

    for student_id in students:

        # Pick a random course
        course_id = random.choice(courses)

        # Select modules belonging to this course
        course_modules = [m[0] for m in modules if m[1] == course_id]

        # Pick a random module from that course
        if course_modules:
            module_id = random.choice(course_modules)
        else:
            # fallback: pick ANY module
            module_id = random.choice(modules)[0]

        level_id = random.choice(levels)
        qualification_id = random.choice(qualifications)
        status = random.choice(statuses)

        # Academic year randomly between 2021–2025
        academic_year = random.randint(2021, 2025)

        # Random enrollment date within the academic year
        start = date(academic_year, 1, 1)
        end = date(academic_year, 12, 31)
        delta_days = random.randint(0, (end - start).days)
        enrollment_date = start + timedelta(days=delta_days)

        credits = random.choice([10, 12, 15, 20])

        enrollments.append(
            (student_id, course_id, module_id, academic_year,
             level_id, qualification_id, status, enrollment_date, credits)
        )

    cursor.executemany("""
        INSERT INTO student_enrollment
        (student_id, course_id, module_id, academic_year,
         level_id, qualification_id, status, enrollment_date, credits)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, enrollments)

    print(f"{len(enrollments)} student enrollments inserted.")




# ==========================
# MAIN
# ==========================
def main():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    insert_base_data(cursor)  # Departments + roles

    insert_levels(cursor)  # MUST come early
    insert_qualifications(cursor)  # MUST come early

    insert_courses_and_departments(cursor)  # Uses levels + qualifications
    insert_modules(cursor)  # Uses courses + levels

    insert_staff_courses_modules(cursor)  # Needs modules
    insert_students_data(cursor)  # Needs levels + courses

    insert_student_enrollments(cursor)  # SAFE HERE
    conn.commit()

    insert_shuttle_data(cursor)
    insert_bus_allocations(cursor)
    insert_applicant_data(cursor)
    insert_lecturer_module_assignments(cursor)

    conn.commit()
    cursor.close()
    conn.close()
    print("\nAll data generation completed successfully.")


if __name__ == "__main__":
    main()
