from flask import request, jsonify
from app import app
from marshmallow import Schema, fields
from modules.models.account import AccountType
from modules.utils.db import db
from modules.utils.route_utils import fetch_session, protected_route


class CreateCourseSchema(Schema):
    course_code = fields.String(required=True)
    course_name = fields.String(required=True)
    lecturer_id = fields.Int(required=True)
    semester = fields.Int(required=True)


class UpdateCourseSchema(Schema):
    course_name = fields.String(required=False)
    lecturer_id = fields.Int(required=False)
    semester = fields.Int(required=False)


@app.route("/courses", methods=["POST"])
@protected_route(roles=[AccountType.Admin])
def create_course():
    body = CreateCourseSchema().load(request.get_json(force=True))
    db_cursor = db.cursor()

    # Find if the course code already exists.
    db_cursor.execute(
        "SELECT * FROM Course WHERE course_code = %s", (body["course_code"],)
    )

    if db_cursor.fetchone():
        return (
            jsonify({"message": "There is already a course with that course code!"}),
            400,
        )

    # Check if the lecturer exists.
    db_cursor.execute(
        "SELECT * FROM Account WHERE id = %s AND account_type = %s",
        (body["lecturer_id"], AccountType.Lecturer.value),
    )
    if not db_cursor.fetchone():
        return (
            jsonify({"message": "There is no lecturer with that ID!"}),
            400,
        )

    # Create the course.
    db_cursor.execute(
        "INSERT INTO Course (course_code, course_name, lecturer_id, semester) VALUES (%s, %s, %s, %s)",
        (
            body["course_code"],
            body["course_name"],
            body["lecturer_id"],
            body["semester"],
        ),
    )

    db.commit()
    course_id = db_cursor.lastrowid
    return jsonify({"course_id": course_id}), 201


@app.route("/courses/<string:course_code>", methods=["PATCH"])
@protected_route(roles=[AccountType.Admin])
def update_course(course_code: str):
    body = UpdateCourseSchema().load(request.get_json(force=True))
    db_cursor = db.cursor()

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the lecturer exists.
    if body.get("lecturer_id"):
        db_cursor.execute(
            "SELECT * FROM Account WHERE id = %s AND account_type = %s",
            (body["lecturer_id"], AccountType.Lecturer.value),
        )
        if not db_cursor.fetchone():
            return (
                jsonify({"message": "There is no lecturer with that ID!"}),
                400,
            )

    # Update the course.
    db_cursor.execute(
        "UPDATE Course SET course_name = %s, lecturer_id = %s, semester = %s WHERE course_code = %s",
        (
            body.get("course_name", course["course_name"]),
            body.get("lecturer_id", course["lecturer_id"]),
            body.get("semester", course["semester"]),
            course_code,
        ),
    )

    db.commit()
    return jsonify({"message": "Course updated!"}), 200


@app.route("/courses", methods=["GET"])
@protected_route()
def get_course():
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM Course")
    courses = db_cursor.fetchall()
    return jsonify(courses), 200


@app.route("/courses/student/<int:student_id>", methods=["GET"])
@protected_route()
def get_courses_for_student(student_id: int):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    if session["account_type"] == AccountType.Student.name:
        student_details = db_cursor.execute(
            "SELECT * FROM StudentDetails WHERE account_id = %s", (session["sub"],)
        ).fetchone()

        if student_id != student_details["student_id"]:
            return jsonify({"message": "You can only view your own courses!"}), 403

    db_cursor.execute(
        "SELECT * FROM Course WHERE course_code IN (SELECT course_code FROM Enrollment WHERE student_id = %s)",
        (student_id,),
    )

    courses = db_cursor.fetchall()
    if not len(courses):
        return jsonify({"message": "There are no courses for this student!"}), 404
    return jsonify(courses), 200


@app.route("/courses/lecturer/<int:lecturer_id>", methods=["GET"])
@protected_route()
def get_courses_for_lecturer(lecturer_id: int):
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM Course WHERE lecturer_id = %s", (lecturer_id,))

    courses = db_cursor.fetchall()
    if not len(courses):
        return jsonify({"message": "There are no courses for this lecturer!"}), 404
    return jsonify(courses), 200


@app.route("/courses/register/<string:course_code>", methods=["POST"])
@protected_route([AccountType.Student])
def register_for_course(course_code: str):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    # Fetch StudentDetails record
    student_details = db_cursor.execute(
        "SELECT * FROM StudentDetails WHERE account_id = %s", (session["sub"],)
    ).fetchone()

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the student is already enrolled in the course.
    db_cursor.execute(
        "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], course_code),
    )
    if db_cursor.fetchone():
        return (
            jsonify({"message": "You are already enrolled in this course!"}),
            400,
        )

    # Register the student for the course.
    db_cursor.execute(
        "INSERT INTO Enrollment (student_id, course_code) VALUES (%s, %s)",
        (student_details["student_id"], course_code),
    )

    db.commit()
    return jsonify({"message": "You have been registered for the course!"}), 201


@app.route("/courses/deregister/<string:course_code>", methods=["DELETE"])
@protected_route([AccountType.Student])
def deregister_from_course(course_code: str):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    # Fetch StudentDetails record
    student_details = db_cursor.execute(
        "SELECT * FROM StudentDetails WHERE account_id = %s", (session["sub"],)
    ).fetchone()

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the student is enrolled in the course.
    db_cursor.execute(
        "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], course_code),
    )
    if not db_cursor.fetchone():
        return (
            jsonify({"message": "You are not enrolled in this course!"}),
            400,
        )

    # Deregister the student from the course.
    db_cursor.execute(
        "DELETE FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], course_code),
    )

    db.commit()
    return jsonify({"message": "You have been deregistered from the course!"}), 200


@app.route("/courses/<string:course_code>/members", methods=["GET"])
@protected_route()
def get_course_members(course_code: str):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    if session["account_type"] == AccountType.Student.name:
        student_details = db_cursor.execute(
            "SELECT * FROM StudentDetails WHERE account_id = %s", (session["sub"],)
        ).fetchone()

        db_cursor.execute(
            "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
            (student_details["student_id"], course_code),
        )
        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view members for your courses!"}),
                403,
            )

    db_cursor.execute(
        "SELECT * FROM StudentDetails WHERE student_id IN (SELECT student_id FROM Enrollment WHERE course_code = %s)",
        (course_code,),
    )

    members = db_cursor.fetchall()
    if not len(members):
        return jsonify({"message": "There are no members for this course!"}), 404
    return jsonify(members), 200
