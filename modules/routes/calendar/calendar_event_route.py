import traceback
from flask import request, jsonify
from app import app
from modules.models.account import AccountType
from modules.routes.courses.courses_route import (
    _check_course_visibility,
    _fetch_student_details_from_session,
)
from modules.routes.calendar.calendar_event_schema import (
    CalendarEventSchema,
    DateRangeSchema,
)
from modules.utils.db import db
from modules.utils.route_utils import authenticate, fetch_session, protected_route


@app.route("/course/<string:course_code>/calendar", methods=["POST", "GET"])
@protected_route()
def handle_course_calendar(course_code):
    if request.method == "POST":
        return create_calendar_event(course_code)
    elif request.method == "GET":
        return get_course_calendar_events(course_code)


def create_calendar_event(course_code: str):
    body = CalendarEventSchema().load(request.get_json(force=True))
    auth_res = authenticate([AccountType.Lecturer, AccountType.Admin])
    if auth_res:
        return auth_res
    session = fetch_session()
    if session["account_type"] == AccountType.Student.name:
        return (
            jsonify(
                {
                    "message": "Students are not allowed to create a course calendar event"
                }
            ),
            403,
        )

    db_cursor = db.cursor(dictionary=True)
    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only create a calendar event for your own courses!",
        },
    )

    if visibility_res:
        return visibility_res

    try:
        db_cursor.execute(
            "INSERT INTO CalendarEvent (course_id, date, event_name) VALUES (%s, %s, %s)",
            (body["course_id"], body["date"], body["event_name"]),
        )
        db.commit()
        return jsonify({"message": "Calendar event created successfully"}), 201
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return jsonify({"message": f"Failed to create calendar event: {str(e)}"}), 500


def get_course_calendar_events(course_id, course_code):
    auth_res = authenticate([AccountType.Lecturer, AccountType.Admin])
    if auth_res:
        return auth_res

    db_cursor = db.cursor(dictionary=True)
    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only get a calendar event for your own courses!",
            "student_err": "You can only get a calendar event for your enrolled courses!",
        },
    )
    if visibility_res:
        return visibility_res

    # Retrieve all calendar events
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM CalendarEvent WHERE course_id = %s", (course_id,))
    events = db_cursor.fetchall()
    if not events:
        return jsonify({"message": "No calendar events found for this course"}), 404
    return jsonify(events), 200


@app.route(
    "/course/<string:course_code>/calendar/student/<int:student_id>",
    methods=["GET"],
)
@protected_route()
def get_student_calendar_events(course_code: str, student_id: int):
    session = fetch_session()

    if session["account_type"] == AccountType.Student.name:
        student_details = _fetch_student_details_from_session(session)
        if student_details["student_id"] != student_id:
            return (
                jsonify({"message": "Unauthorized access to student calendar events"}),
                403,
            )
    elif session["account_type"] == AccountType.Lecturer.name:
        visibility_res = _check_course_visibility(
            session,
            course_code,
            err_msgs={
                "lecturer_err": "You can only get a student's calendar events for your own courses!",
            },
        )

        if visibility_res:
            return visibility_res

    # Parse the request body to get the start date and end date
    request_data = request.get_json(force=True)
    date_range = DateRangeSchema().load(request_data)

    # Extract start date and end date from the request data
    start_date = date_range.get("start_date")
    end_date = date_range.get("end_date")

    # Construct the query based on the provided start and end dates
    query = "SELECT * FROM CalendarEvent WHERE course_id IN (SELECT course_id FROM Enrollment WHERE student_id = %s)"
    params = [student_id]

    if start_date is not None and end_date is not None:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date is not None:
        query += " AND date >= %s"
        params.append(start_date)
    elif end_date is not None:
        query += " AND date <= %s"
        params.append(end_date)

    # Retrieve calendar events for the student based on the constructed query
    db_cursor = db.cursor(dictionary=True)
    db_cursor.execute(query, params)
    events = db_cursor.fetchall()

    if not events:
        return (
            jsonify(
                {
                    "message": "No calendar events found for this student within the specified date range"
                }
            ),
            404,
        )

    # Convert the events data into JSON format and return
    return jsonify(events), 200
