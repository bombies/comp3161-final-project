from flask import request, jsonify
from app import app
from marshmallow import Schema, fields
from modules.models.account import AccountType
from modules.utils.db import db
from modules.utils.route_utils import protected_route


class CreateCourseSchema(Schema):
    course_code = fields.String(required=True)
    course_name = fields.String(required=True)
    lecturer_id = fields.Int(required=True)
    semester = fields.Int(required=True)


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
