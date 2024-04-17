from flask import request, jsonify
from app import app
from modules.models.account import AccountType
from modules.routes.calendar.calendar_event_schema import (
    CalendarEventSchema,

)
from modules.utils.db import db
from modules.utils.route_utils import authenticate, fetch_session, protected_route

@app.route("/calendar", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer])
def create_calendar_event():
    body = CalendarEventSchema().load(request.get_json(force=True))

    db_cursor = db.cursor()
    try:
        db_cursor.execute(
            "INSERT INTO CalendarEvent (course_id, date, event_name, event_no) VALUES (%s, %s, %s, %s)",
            (body["course_id"], body["date"], body["event_name"], body["event_no"]),
        )
        db.commit()
        return jsonify({"message": "Calendar event created successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to create calendar event: {str(e)}"}), 500

@app.route("/calendar/events/course/<string:course_id>", methods=["GET"])
def get_course_calendar_events():
    # Retrieve all calendar events
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM CalendarEvent WHERE course_id = %s", (course_id,))
    events = db_cursor.fetchall()
    if not events:
        return jsonify({"message": "No calendar events found for this course"}), 404
    # Convert the events data into JSON format and return
    return jsonify(events), 200
    # Return data as per requirements

@app.route("/calendar/events/student/<int:student_id>/date/<date:date>", methods=["GET"])
def get_student_calendar_events(student_id, date):
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM CalendarEvent WHERE date = %s AND course_id IN (SELECT course_id FROM Enrollment WHERE student_id = %s)", (date, student_id))
    events = db_cursor.fetchall()
    if not events:
        return jsonify({"message": "No calendar events found for this student on this date"}), 404
    # Convert the events data into JSON format and return
    return jsonify(events), 200


