create database university_system;
use university_system;


CREATE TABLE IF NOT EXISTS qualifications (
    qualification_id INT PRIMARY KEY AUTO_INCREMENT,
    qualification_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS levels (
    level_id INT PRIMARY KEY AUTO_INCREMENT,
    level_name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS staff_roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100) NOT NULL,
    department_id INT,
    qualification_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (qualification_id) REFERENCES qualifications(qualification_id)
);

CREATE TABLE IF NOT EXISTS modules (
    module_id INT PRIMARY KEY AUTO_INCREMENT,
    module_name VARCHAR(100) NOT NULL,
    course_id INT,
    level_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (level_id) REFERENCES levels(level_id)
);

-- ===========================
-- 2. Main Entities
-- ===========================

CREATE TABLE IF NOT EXISTS staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(50),
	role_id INT,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (role_id) REFERENCES staff_roles(role_id)
);

CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_number VARCHAR(20) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(20),
    birthdate DATE,
    level_id INT,
    course_id INT,
    department_id INT,
    email VARCHAR(150),
    phone VARCHAR(50),
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS buses (
    bus_id INT PRIMARY KEY AUTO_INCREMENT,
    bus_number VARCHAR(20),
    capacity INT
);

-- ===========================
-- 3. Assignment & Relationship Tables
-- ===========================

CREATE TABLE IF NOT EXISTS lecturer_module_assignment (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    staff_id INT,
    module_id INT,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);

CREATE TABLE if not exists student_enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    module_id INT,
    academic_year INT,
    level_id INT,
    qualification_id INT,
    status VARCHAR(20),
    enrollment_date DATE,
    credits INT,
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id),
    FOREIGN KEY(module_id) REFERENCES modules(module_id),
    FOREIGN KEY(level_id) REFERENCES levels(level_id),
    FOREIGN KEY(qualification_id) REFERENCES qualifications(qualification_id)
);
DELIMITER $$

CREATE PROCEDURE enroll_student (
    IN p_student_id INT,
    IN p_course_id INT,
    IN p_module_id INT,
    IN p_level_id INT,
    IN p_qualification_id INT,
    IN p_academic_year INT,
    IN p_status VARCHAR(20)
)
BEGIN
    INSERT INTO student_enrollment (
        student_id,
        course_id,
        module_id,
        academic_year,
        level_id,
        qualification_id,
        status,
        enrollment_date,
        credits
    )
    VALUES (
        p_student_id,
        p_course_id,
        p_module_id,
        p_academic_year,
        p_level_id,
        p_qualification_id,
        p_status,
        CURDATE(),
        0
    );
END $$

DELIMITER ;


CREATE TABLE IF NOT EXISTS student_marks (
    mark_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    module_id INT,
    test_score DECIMAL(5,2),
    exam_score DECIMAL(5,2),
    final_score DECIMAL(5,2),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);

CREATE TABLE IF NOT EXISTS student_residential (
    residential_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    residence_name VARCHAR(100),
    room_number VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS shuttle_points (
    point_id INT PRIMARY KEY AUTO_INCREMENT,
    point_name VARCHAR(100),
    location VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS bus_allocations (
    allocation_id INT PRIMARY KEY AUTO_INCREMENT,
    bus_id INT,
    point_id INT,
    allocation_time TIME,
    FOREIGN KEY (bus_id) REFERENCES buses(bus_id),
    FOREIGN KEY (point_id) REFERENCES shuttle_points(point_id)
);

CREATE TABLE IF NOT EXISTS applicant_status (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    application_status VARCHAR(50),
    application_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL UNIQUE
);

show tables;
