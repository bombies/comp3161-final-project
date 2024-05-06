from flask import request, jsonify
from app import app
from modules.models.account import AccountType
from modules.routes.calendar.calendar_event_schema import (
    CalendarEventSchema,
    DateRangeSchema,

)
from modules.utils.db import db
from modules.utils.route_utils import authenticate, fetch_session, protected_route

@app.route("/calendar/<string:course_id>", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer])
def create_calendar_event(course_id: str):
    body = CalendarEventSchema().load(request.get_json(force=True))

    db_cursor = db.cursor()
    try:
        db_cursor.execute(
            "INSERT INTO CalendarEvent (course_id, date, event_name) VALUES (%s, %s, %s)",
            (body["course_id"], body["date"], body["event_name"]),
        )
        db.commit()
        return jsonify({"message": "Calendar event created successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to create calendar event: {str(e)}"}), 500

@app.route("/calendar/events/course/<string:course_id>", methods=["GET"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer, AccountType.student])
def get_course_calendar_events(course_id):
    # Retrieve all calendar events
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM CalendarEvent WHERE course_id = %s", (course_id,))
    events = db_cursor.fetchall()
    if not events:
        return jsonify({"message": "No calendar events found for this course"}), 404
    # Convert the events data into JSON format and return
    return jsonify(events), 200
    # Return data as per requirements

@app.route("/calendar/events/student/<int:student_id>", methods=["GET"])
@protected_route([AccountType.Student, AccountType.Admin])
def get_student_calendar_events(student_id):
    session = fetch_session()
    # Check if the session is a student account
    if session.get("account_type") == AccountType.Student:
        # Check if the student ID from the session matches the ID passed to the function
        if session.get("student_id") != student_id:
            return jsonify({"message": "Unauthorized access to student calendar events"}), 403

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
    db_cursor = db.cursor()
    db_cursor.execute(query, params)
    events = db_cursor.fetchall()

    if not events:
        return jsonify({"message": "No calendar events found for this student within the specified date range"}), 404

    # Convert the events data into JSON format and return
    return jsonify(events), 200



