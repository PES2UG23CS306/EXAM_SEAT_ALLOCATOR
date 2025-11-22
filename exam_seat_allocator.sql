

The complete SQL script containing all CREATE, INSERT, TRIGGER, PROCEDURE, FUNCTION, 
and QUERY statements used in this project is provided as a separate file:

**File Name:** PES2UG23CS275_PES2UG23CS306.sql




-- **To execute the complete script:**
-- ```bash
-- mysql -u root -p < PES2UG23CS275_PES2UG23CS306.sql
-- ```



-- =====================================================
-- EXAM HALL SEAT ALLOCATOR AND CHECKER
-- Complete SQL Script
-- Team: PES2UG23CS275 (Khizer Pasha), PES2UG23CS306 (Likith N)
-- =====================================================

-- =====================================================
-- DATABASE CREATION
-- =====================================================

CREATE DATABASE IF NOT EXISTS exam_seat_allocator;
USE exam_seat_allocator;

-- =====================================================
-- TABLE CREATION (DDL)
-- =====================================================

-- Students Table
CREATE TABLE students (
  student_id INT PRIMARY KEY,
  srn VARCHAR(20) NOT NULL UNIQUE,
  full_name VARCHAR(100) NOT NULL,
  department VARCHAR(50) NOT NULL,
  year_of_study TINYINT NOT NULL CHECK (year_of_study BETWEEN 1 AND 8),
  email VARCHAR(150) UNIQUE,
  phone VARCHAR(20),
  gender CHAR(1) DEFAULT 'O',
  dob DATE
);

-- Exams Table
CREATE TABLE exams (
  exam_id INT PRIMARY KEY,
  course_code VARCHAR(20) NOT NULL,
  course_name VARCHAR(150) NOT NULL,
  exam_date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  total_marks INT DEFAULT 100 CHECK (total_marks > 0),
  UNIQUE (course_code, exam_date)
);

-- Halls Table
CREATE TABLE halls (
  hall_id INT PRIMARY KEY,
  hall_name VARCHAR(100) NOT NULL UNIQUE,
  capacity INT NOT NULL CHECK (capacity > 0),
  location VARCHAR(150)
);

-- Seats Table
CREATE TABLE seats (
  seat_id INT PRIMARY KEY,
  hall_id INT NOT NULL,
  seat_number VARCHAR(10) NOT NULL,
  is_accessible BOOLEAN NOT NULL DEFAULT FALSE,
  remarks VARCHAR(255),
  UNIQUE (hall_id, seat_number),
  CONSTRAINT fk_seats_halls FOREIGN KEY (hall_id)
    REFERENCES halls(hall_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Invigilators Table
CREATE TABLE invigilators (
  invigilator_id INT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE,
  phone VARCHAR(20),
  assigned BOOLEAN DEFAULT FALSE
);

-- Hall Assignments Table
CREATE TABLE hall_assignments (
  assignment_id INT PRIMARY KEY,
  exam_id INT NOT NULL,
  hall_id INT NOT NULL,
  invigilator_id INT,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  UNIQUE (exam_id, hall_id),
  CONSTRAINT fk_ha_exam FOREIGN KEY (exam_id)
    REFERENCES exams(exam_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_ha_hall FOREIGN KEY (hall_id)
    REFERENCES halls(hall_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_ha_inv FOREIGN KEY (invigilator_id)
    REFERENCES invigilators(invigilator_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- Allocations Table
CREATE TABLE allocations (
  allocation_id INT PRIMARY KEY,
  exam_id INT NOT NULL,
  student_id INT,
  seat_id INT NOT NULL,
  allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_alloc_exam FOREIGN KEY (exam_id)
    REFERENCES exams(exam_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_alloc_student FOREIGN KEY (student_id)
    REFERENCES students(student_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_alloc_seat FOREIGN KEY (seat_id)
    REFERENCES seats(seat_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  UNIQUE (exam_id, seat_id),
  UNIQUE (exam_id, student_id)
);

-- Seat Checks Table
CREATE TABLE seat_checks (
  check_id INT PRIMARY KEY,
  allocation_id INT NOT NULL,
  checked_by INT,
  status VARCHAR(20) NOT NULL DEFAULT 'OK',
  remarks VARCHAR(255),
  checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_check_alloc FOREIGN KEY (allocation_id)
    REFERENCES allocations(allocation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_check_inv FOREIGN KEY (checked_by)
    REFERENCES invigilators(invigilator_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- =====================================================
-- VIEW TABLE STRUCTURES
-- =====================================================

DESC students;
DESC exams;
DESC halls;
DESC seats;
DESC invigilators;
DESC hall_assignments;
DESC allocations;
DESC seat_checks;

-- =====================================================
-- SAMPLE DATA INSERTION (DML)
-- =====================================================

-- Insert Students
INSERT INTO students (student_id, srn, full_name, department, year_of_study, email, phone, gender, dob) VALUES
(1,'PES2UG23CS101','Arjun Kumar','CSE',2,'arjun.kumar@example.edu','+91-9876501010','M','2004-05-12'),
(2,'PES2UG23CS102','Bhavana Reddy','CSE',2,'bhavana.reddy@example.edu','+91-9876501020','F','2004-08-21'),
(3,'PES2UG23CS103','Chirag Patel','CSE',2,'chirag.patel@example.edu','+91-9876501030','M','2004-11-02'),
(4,'PES2UG23CS104','Deepa Nair','CSE',2,'deepa.nair@example.edu','+91-9876501040','F','2004-02-18'),
(5,'PES2UG23CS105','Eshwar Singh','CSE',2,'eshwar.singh@example.edu','+91-9876501050','M','2004-07-30');

-- Insert Exams
INSERT INTO exams (exam_id, course_code, course_name, exam_date, start_time, end_time, total_marks) VALUES
(1,'CS201','Data Structures','2025-09-20','09:00:00','12:00:00',100),
(2,'CS202','Database Systems','2025-09-22','14:00:00','17:00:00',100),
(3,'CS203','Operating Systems','2025-09-24','09:00:00','12:00:00',100),
(4,'CS204','Computer Networks','2025-09-26','14:00:00','17:00:00',100),
(5,'CS205','Algorithms','2025-09-28','09:00:00','12:00:00',100);

-- Insert Halls
INSERT INTO halls (hall_id, hall_name, capacity, location) VALUES
(1,'LH-101',60,'Main Building Ground Floor'),
(2,'LH-102',40,'Main Building First Floor'),
(3,'CH-Auditorium',120,'Central Block'),
(4,'LH-201',50,'Main Building Second Floor'),
(5,'Seminar Hall',80,'Block B');

-- Insert Seats
INSERT INTO seats (seat_id, hall_id, seat_number, is_accessible, remarks) VALUES
(1,1,'A1',FALSE,'Front row left'),
(2,1,'A2',FALSE,'Front row center'),
(3,1,'A3',TRUE,'Wheelchair access'),
(4,1,'A4',FALSE,'Second row'),
(5,1,'A5',FALSE,'Second row'),
(6,2,'B1',FALSE,'Near door'),
(7,2,'B2',FALSE,'Near window'),
(8,2,'B3',FALSE,'Middle row'),
(9,2,'B4',FALSE,'Corner seat'),
(10,2,'B5',TRUE,'Accessible seat');

-- Insert Invigilators
INSERT INTO invigilators (invigilator_id, full_name, email, phone, assigned) VALUES
(1,'Prof. Ramesh Kumar','ramesh.kumar@college.edu','+91-9444001111',FALSE),
(2,'Dr. Anita Sharma','anita.sharma@college.edu','+91-9444002222',FALSE),
(3,'Mr. Suresh Rao','suresh.rao@college.edu','+91-9444003333',FALSE),
(4,'Ms. Priya Mehta','priya.mehta@college.edu','+91-9444004444',FALSE),
(5,'Dr. Ajay Varma','ajay.varma@college.edu','+91-9444005555',FALSE);

-- Insert Hall Assignments
INSERT INTO hall_assignments (assignment_id, exam_id, hall_id, invigilator_id, start_time, end_time) VALUES
(1,1,1,1,'08:30:00','12:30:00'),
(2,2,2,2,'13:30:00','17:30:00'),
(3,3,3,3,'08:30:00','12:30:00'),
(4,4,4,4,'13:30:00','17:30:00'),
(5,5,5,5,'09:00:00','13:00:00');

-- Insert Allocations
INSERT INTO allocations (allocation_id, exam_id, student_id, seat_id) VALUES
(1,1,1,1),
(2,1,2,2),
(3,1,3,3),
(4,1,4,4),
(5,1,5,5);

-- Insert Seat Checks
INSERT INTO seat_checks (check_id, allocation_id, checked_by, status, remarks) VALUES
(1,1,1,'OK','All correct'),
(2,2,1,'OK','All correct'),
(3,3,2,'MISMATCH','SRN mismatch on admit card'),
(4,4,2,'ABSENT','Student did not turn up'),
(5,5,3,'OK','All correct');

-- =====================================================
-- VIEW ALL DATA
-- =====================================================

SELECT * FROM students;
SELECT * FROM exams;
SELECT * FROM halls;
SELECT * FROM seats;
SELECT * FROM invigilators;
SELECT * FROM hall_assignments;
SELECT * FROM allocations;
SELECT * FROM seat_checks;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger 1: Update Invigilator Status
DELIMITER //
CREATE TRIGGER trg_update_invigilator_status
AFTER INSERT ON hall_assignments
FOR EACH ROW
BEGIN
    UPDATE invigilators
    SET assigned = TRUE
    WHERE invigilator_id = NEW.invigilator_id;
END;
//
DELIMITER ;

-- Trigger 2: Auto Create Seat Check
DELIMITER //
CREATE TRIGGER trg_auto_seat_check
AFTER INSERT ON allocations
FOR EACH ROW
BEGIN
    DECLARE next_check_id INT;
    
    SELECT IFNULL(MAX(check_id), 0) + 1 INTO next_check_id
    FROM (SELECT check_id FROM seat_checks) AS temp;
    
    INSERT INTO seat_checks (check_id, allocation_id, checked_by, status, remarks)
    VALUES (next_check_id, NEW.allocation_id, NULL, 'PENDING', 'Awaiting verification');
END;
//
DELIMITER ;

-- =====================================================
-- TRIGGER TESTING
-- =====================================================

-- Test Trigger 1: trg_update_invigilator_status
SELECT invigilator_id, full_name, assigned FROM invigilators WHERE invigilator_id = 3;
INSERT INTO hall_assignments VALUES (6, 1, 2, 3, '09:00:00', '12:00:00');
SELECT invigilator_id, full_name, assigned FROM invigilators WHERE invigilator_id = 3;

-- Test Trigger 2: trg_auto_seat_check
SELECT COUNT(*) FROM seat_checks;
INSERT INTO allocations (allocation_id, exam_id, student_id, seat_id) VALUES (10, 2, 3, 6);
SELECT * FROM seat_checks WHERE allocation_id = 10;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Procedure 1: Allocate Student to Seat
DELIMITER //
CREATE PROCEDURE allocate_student_to_seat(
    IN p_exam_id INT,
    IN p_student_id INT,
    IN p_seat_id INT
)
BEGIN
    DECLARE seat_taken INT;
    DECLARE student_taken INT;
    DECLARE next_id INT;
    
    SELECT IFNULL(MAX(allocation_id), 0) + 1 INTO next_id FROM allocations;
    
    SELECT COUNT(*) INTO seat_taken
    FROM allocations
    WHERE exam_id = p_exam_id AND seat_id = p_seat_id;
    
    SELECT COUNT(*) INTO student_taken
    FROM allocations
    WHERE exam_id = p_exam_id AND student_id = p_student_id;
    
    IF seat_taken = 0 AND student_taken = 0 THEN
        INSERT INTO allocations (allocation_id, exam_id, student_id, seat_id)
        VALUES (next_id, p_exam_id, p_student_id, p_seat_id);
        SELECT 'Allocation Successful' AS message;
    ELSE
        SELECT 'Seat or student already allocated for this exam' AS message;
    END IF;
END;
//
DELIMITER ;

-- Procedure 2: Remove Allocation
DELIMITER //
CREATE PROCEDURE remove_allocation(IN p_allocation_id INT)
BEGIN
    DELETE FROM allocations WHERE allocation_id = p_allocation_id;
    SELECT CONCAT('Allocation ', p_allocation_id, ' removed successfully') AS message;
END;
//
DELIMITER ;

-- =====================================================
-- PROCEDURE TESTING
-- =====================================================

-- Test Procedure 1: allocate_student_to_seat
CALL allocate_student_to_seat(2, 3, 6);
SELECT * FROM allocations WHERE exam_id = 2;

-- Test Procedure 2: remove_allocation
CALL remove_allocation(5);
SELECT * FROM allocations;

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function 1: Count Allocated Students
DELIMITER //
CREATE FUNCTION count_allocated_students(p_exam_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total
    FROM allocations
    WHERE exam_id = p_exam_id;
    RETURN total;
END;
//
DELIMITER ;

-- Function 2: Hall Occupancy
DELIMITER //
CREATE FUNCTION hall_occupancy(p_exam_id INT, p_hall_id INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    DECLARE total_seats INT;
    DECLARE used_seats INT;
    DECLARE percent DECIMAL(5,2);
    
    SELECT COUNT(*) INTO total_seats FROM seats WHERE hall_id = p_hall_id;
    
    SELECT COUNT(*) INTO used_seats
    FROM allocations a
    JOIN seats s ON a.seat_id = s.seat_id
    WHERE a.exam_id = p_exam_id AND s.hall_id = p_hall_id;
    
    IF total_seats = 0 THEN
        SET percent = 0;
    ELSE
        SET percent = (used_seats / total_seats) * 100;
    END IF;
    
    RETURN percent;
END;
//
DELIMITER ;

-- Function 3: Get Student Seat
DELIMITER //
CREATE FUNCTION get_student_seat(p_srn VARCHAR(20))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE seat_info VARCHAR(255);
    
    SELECT CONCAT(h.hall_name, ' - ', s.seat_number) INTO seat_info
    FROM students st
    JOIN allocations a ON st.student_id = a.student_id
    JOIN seats s ON a.seat_id = s.seat_id
    JOIN halls h ON s.hall_id = h.hall_id
    JOIN exams e ON a.exam_id = e.exam_id
    WHERE st.srn = p_srn
    ORDER BY e.exam_date DESC
    LIMIT 1;
    
    RETURN seat_info;
END;
//
DELIMITER ;

-- =====================================================
-- FUNCTION TESTING
-- =====================================================

-- Test Function 1: count_allocated_students
SELECT count_allocated_students(1) AS 'Total Students in Exam 1';

-- Test Function 2: hall_occupancy
SELECT hall_occupancy(1, 1) AS 'Hall 1 Occupancy %';

-- Test Function 3: get_student_seat
SELECT get_student_seat('PES2UG23CS101') AS 'Next Exam Seat';

-- =====================================================
-- NESTED QUERIES
-- =====================================================

-- Nested Query 1: Students Not Allocated for Exam 1
SELECT student_id, srn, full_name, department
FROM students
WHERE student_id NOT IN (
    SELECT student_id 
    FROM allocations 
    WHERE exam_id = 1
)
ORDER BY srn;

-- Nested Query 2: Available Seats for Exam 2
SELECT 
    h.hall_name,
    s.seat_number,
    s.is_accessible,
    s.remarks
FROM seats s
JOIN halls h ON s.hall_id = h.hall_id
WHERE s.hall_id IN (
    SELECT hall_id 
    FROM hall_assignments 
    WHERE exam_id = 2
)
AND s.seat_id NOT IN (
    SELECT seat_id 
    FROM allocations 
    WHERE exam_id = 2
)
ORDER BY h.hall_name, s.seat_number;

-- Nested Query 3: Halls with Maximum Allocations
SELECT h.hall_name, COUNT(a.allocation_id) AS total_allocations
FROM halls h
JOIN seats s ON h.hall_id = s.hall_id
JOIN allocations a ON s.seat_id = a.seat_id
GROUP BY h.hall_id, h.hall_name
HAVING COUNT(a.allocation_id) = (
    SELECT MAX(allocation_count)
    FROM (
        SELECT COUNT(a2.allocation_id) AS allocation_count
        FROM halls h2
        JOIN seats s2 ON h2.hall_id = s2.hall_id
        JOIN allocations a2 ON s2.seat_id = a2.seat_id
        GROUP BY h2.hall_id
    ) AS subquery
);

-- =====================================================
-- JOIN QUERIES
-- =====================================================

-- Join Query 1: Complete Allocation Details
SELECT 
    a.allocation_id,
    s.srn,
    s.full_name AS student_name,
    s.department,
    e.course_code,
    e.course_name,
    e.exam_date,
    h.hall_name,
    se.seat_number,
    i.full_name AS invigilator_name
FROM allocations a
JOIN students s ON a.student_id = s.student_id
JOIN exams e ON a.exam_id = e.exam_id
JOIN seats se ON a.seat_id = se.seat_id
JOIN halls h ON se.hall_id = h.hall_id
LEFT JOIN hall_assignments ha ON ha.exam_id = e.exam_id AND ha.hall_id = h.hall_id
LEFT JOIN invigilators i ON ha.invigilator_id = i.invigilator_id
ORDER BY e.exam_date, h.hall_name, se.seat_number;

-- Join Query 2: Students with Accessible Seats
SELECT 
    s.srn,
    s.full_name,
    s.department,
    e.course_code,
    e.exam_date,
    h.hall_name,
    se.seat_number,
    se.remarks AS seat_remarks
FROM students s
JOIN allocations a ON s.student_id = a.student_id
JOIN seats se ON a.seat_id = se.seat_id
JOIN halls h ON se.hall_id = h.hall_id
JOIN exams e ON a.exam_id = e.exam_id
WHERE se.is_accessible = TRUE
ORDER BY e.exam_date, s.full_name;

-- Join Query 3: Invigilator Workload
SELECT 
    i.invigilator_id,
    i.full_name,
    i.email,
    i.assigned,
    COUNT(ha.assignment_id) AS total_assignments,
    GROUP_CONCAT(DISTINCT e.course_code ORDER BY e.exam_date SEPARATOR ', ') AS assigned_exams
FROM invigilators i
LEFT JOIN hall_assignments ha ON i.invigilator_id = ha.invigilator_id
LEFT JOIN exams e ON ha.exam_id = e.exam_id
GROUP BY i.invigilator_id, i.full_name, i.email, i.assigned
ORDER BY total_assignments DESC;

-- =====================================================
-- AGGREGATE QUERIES
-- =====================================================

-- Aggregate Query 1: Hall-wise Allocation Statistics
SELECT 
    h.hall_name,
    h.capacity,
    COUNT(DISTINCT se.seat_id) AS total_seats,
    COUNT(a.allocation_id) AS seats_allocated,
    ROUND((COUNT(a.allocation_id) / COUNT(DISTINCT se.seat_id)) * 100, 2) AS occupancy_percentage
FROM halls h
LEFT JOIN seats se ON h.hall_id = se.hall_id
LEFT JOIN allocations a ON se.seat_id = a.seat_id
GROUP BY h.hall_id, h.hall_name, h.capacity
ORDER BY occupancy_percentage DESC;

-- Aggregate Query 2: Exam-wise Student Count
SELECT 
    e.exam_id,
    e.course_code,
    e.course_name,
    e.exam_date,
    COUNT(a.allocation_id) AS total_students_allocated,
    COUNT(DISTINCT se.hall_id) AS halls_used
FROM exams e
LEFT JOIN allocations a ON e.exam_id = a.exam_id
LEFT JOIN seats se ON a.seat_id = se.seat_id
GROUP BY e.exam_id, e.course_code, e.course_name, e.exam_date
ORDER BY e.exam_date;

-- Aggregate Query 3: Seat Check Status Summary
SELECT 
    e.course_code,
    e.course_name,
    sc.status,
    COUNT(*) AS status_count
FROM seat_checks sc
JOIN allocations a ON sc.allocation_id = a.allocation_id
JOIN exams e ON a.exam_id = e.exam_id
GROUP BY e.exam_id, e.course_code, e.course_name, sc.status
ORDER BY e.course_code, sc.status;

-- Aggregate Query 4: Department-wise Student Distribution
SELECT 
    department,
    year_of_study,
    COUNT(*) AS student_count,
    COUNT(CASE WHEN gender = 'M' THEN 1 END) AS male_count,
    COUNT(CASE WHEN gender = 'F' THEN 1 END) AS female_count
FROM students
GROUP BY department, year_of_study
ORDER BY department, year_of_study;

-- Aggregate Query 5: Average Marks and Exam Duration
SELECT 
    AVG(total_marks) AS avg_marks,
    MAX(total_marks) AS max_marks,
    MIN(total_marks) AS min_marks,
    AVG(TIMESTAMPDIFF(MINUTE, start_time, end_time)) AS avg_duration_minutes
FROM exams;

-- =====================================================
-- ADDITIONAL USEFUL QUERIES
-- =====================================================

-- Query: Unallocated Students for a Specific Exam
SELECT s.student_id, s.srn, s.full_name FROM students s
WHERE s.student_id NOT IN (SELECT student_id FROM allocations WHERE exam_id = 1)
ORDER BY s.student_id;

-- Query: Free Seats in Assigned Halls for Exam
SELECT seat_id, hall_id, seat_number FROM seats
WHERE seat_id NOT IN (SELECT seat_id FROM allocations WHERE exam_id = 1)
AND hall_id IN (SELECT hall_id FROM hall_assignments WHERE exam_id = 1)
ORDER BY hall_id, seat_number;

-- Query: Seats Filled per Hall (Dashboard)
SELECT h.hall_name, COUNT(a.allocation_id) AS filled
FROM halls h
LEFT JOIN seats s ON s.hall_id = h.hall_id
LEFT JOIN allocations a ON a.seat_id = s.seat_id
GROUP BY h.hall_name;

-- Query: Students per Exam (Dashboard)
SELECT e.course_code, COUNT(a.allocation_id) AS allocated
FROM exams e
LEFT JOIN allocations a ON a.exam_id = e.exam_id
GROUP BY e.course_code;

-- =====================================================
-- END OF SQL SCRIPT
-- =====================================================