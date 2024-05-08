from flask import Flask, jsonify
from app import app
from modules.utils.db import db

db_cursor = db.cursor(dictionary=True)


# Route for all courses with 50 or more students
@app.route("/reports/courses/50students", methods=["GET"])
def courses_50_students():
    query = """
    CREATE OR REPLACE VIEW Courses_With_50_Or_More_Students AS
    SELECT c.course_code, c.course_name, COUNT(e.student_id) AS student_count
    FROM Course c
    JOIN Enrollment e ON c.course_code = e.course_code
    GROUP BY c.course_code
    HAVING COUNT(e.student_id) >= 50;
    """
    db_cursor.execute(query)
    courses = db_cursor.fetchall()
    return jsonify(courses), 200


# Route for all students enrolled in 5 or more courses
@app.route("/reports/students/5courses", methods=["GET"])
def students_5_courses():
    query = """
    CREATE OR REPLACE VIEW Students_Taking_5_Or_More_Courses AS
    SELECT s.student_id, s.gpa, COUNT(e.course_code) AS course_count
    FROM StudentDetails s
    JOIN Enrollment e ON s.student_id = e.student_id
    GROUP BY s.student_id
    HAVING COUNT(e.course_code) >= 5;
    """
    db_cursor.execute(query)
    students = db_cursor.fetchall()
    return jsonify(students), 200


# Route for all lecturers teaching 3 or more courses
@app.route("/reports/lecturers/3courses", methods=["GET"])
def lecturers_3_courses():
    query = """
    CREATE OR REPLACE VIEW Lecturers_Teaching_3_Or_More_Courses AS
    SELECT l.lecturer_id, COUNT(c.course_code) AS course_count
    FROM LecturerDetails l
    JOIN Course c ON l.lecturer_id = c.lecturer_id
    GROUP BY l.lecturer_id
    HAVING COUNT(c.course_code) >= 3;
    """
    db_cursor.execute(query)
    lecturers = db_cursor.fetchall()
    return jsonify(lecturers), 200


# Route for the top 10 most enrolled courses
@app.route("/reports/top10enrolled", methods=["GET"])
def top_10_enrolled_courses():
    query = """
    CREATE OR REPLACE VIEW Top_10_Enrolled_Courses AS
    SELECT c.course_code, c.course_name, COUNT(e.student_id) AS student_count
    FROM Course c
    JOIN Enrollment e ON c.course_code = e.course_code
    GROUP BY c.course_code
    ORDER BY COUNT(e.student_id) DESC
    LIMIT 10;
    """
    db_cursor.execute(query)
    top_courses = db_cursor.fetchall()
    return jsonify(top_courses), 200


# Route for the top 10 students with the highest overall averages
@app.route("/reports/top10students", methods=["GET"])
def top_10_students():
    query = """
    CREATE OR REPLACE VIEW Top_10_Students_Highest_Averages AS
    SELECT s.student_id, s.gpa, AVG(a.grade) AS average_grade
    FROM StudentDetails s
    JOIN AssignmentSubmission a ON s.student_id = a.student_id
    GROUP BY s.student_id
    ORDER BY AVG(a.grade) DESC
    LIMIT 10;
    """
    db_cursor.execute(query)
    top_students = db_cursor.fetchall()
    return jsonify(top_students), 200
