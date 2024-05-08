import pytest
from app import app
from tests.mockers.calendar_mocker import CalendarMocker
from tests.mockers.forum_mocker import ForumMocker
from tests.mockers.account_mocker import AccountMocker
from tests.mockers.course_mocker import CourseMocker
from modules.utils.db import db
import tests.utils as utils

test_client = app.test_client()
forum_mocker = ForumMocker()
account_mocker = AccountMocker()
course_mocker = CourseMocker()
calendar_mocker = CalendarMocker()
admin_token = utils.create_admin_token()


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    db_cursor = db.cursor(dictionary=True)
    # Delete all courses
    db_cursor.execute("DELETE FROM Course")

    # Delete all accounts
    db_cursor.execute("DELETE FROM Account")

    db.commit()


def test_calendar_event_creation():
    # Create a lecturer
    lecturer = AccountMocker.insert_mock_lecturer()
    lecturer_token = utils.create_lecturer_token_from_mock(
        (lecturer["mock_account"], lecturer["mock_details"])
    )

    # Create a course
    course = CourseMocker.insert_mock_course(lecturer)
    course_code = course["course_code"]

    db_cursor = db.cursor(dictionary=True)

    try:
        # Create a calendar event
        event = calendar_mocker.mock_event()
        response = test_client.post(
            f"/course/{course_code}/calendar",
            json={
                "course_id": course["course_code"],
                "event_name": event["event_name"],
                "date": event["date"].isoformat(),
            },
            headers={"Authorization": f"Bearer {lecturer_token}"},
        )

        assert response.status_code == 201

        event_record = response.get_json()
        assert event_record
        assert event_record["event_name"] == event["event_name"]

        # Delete the created event
        db_cursor.execute(
            "DELETE FROM CalendarEvent WHERE event_no = %s", (event_record["event_no"],)
        )
        db.commit()
    finally:
        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (lecturer["account_id"],)
        )
        db.commit()


def test_get_calendar_events():
    # Create a lecturer
    lecturer = AccountMocker.insert_mock_lecturer()
    lecturer_token = utils.create_lecturer_token_from_mock(
        (lecturer["mock_account"], lecturer["mock_details"])
    )

    # Create a course
    course = CourseMocker.insert_mock_course(lecturer)
    course_code = course["course_code"]

    # Create calendar events
    event = CalendarMocker.insert_event(course)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Get the created event
        response = test_client.get(
            f"/course/{course_code}/calendar",
            headers={"Authorization": f"Bearer {lecturer_token}"},
        )
        assert response.status_code == 200

        events = response.get_json()
        assert events
        assert len(events) == 1
        assert events[0]["event_name"] == event["event_name"]
    finally:
        # Delete the created event
        db_cursor.execute(
            "DELETE FROM CalendarEvent WHERE event_no = %s", (event["event_no"],)
        )
        db.commit()

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (lecturer["account_id"],)
        )
        db.commit()


def test_get_student_specific_course_events():
    # Create a student
    student = AccountMocker.insert_mock_student()
    student_token = utils.create_student_token_from_mock(
        (student["mock_account"], student["mock_details"])
    )

    # Create a lecturer
    lecturer = AccountMocker.insert_mock_lecturer()

    # Create courses
    course = CourseMocker.insert_mock_course(lecturer)
    course2 = CourseMocker.insert_mock_course(lecturer)
    course_code = course["course_code"]

    # Enrol student to the courses
    CourseMocker.enrol_mock_student(course, student)
    CourseMocker.enrol_mock_student(course2, student)

    # Create calendar events
    event = CalendarMocker.insert_event(course)
    event2 = CalendarMocker.insert_event(course2)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Get the created event
        response = test_client.get(
            f"/course/{course_code}/calendar/student/{student['student_id']}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={},
        )
        assert response.status_code == 200

        events = response.get_json()
        assert events
        assert len(events) == 1
        assert events[0]["event_name"] == event["event_name"]
        assert events[0]["event_no"] == event["event_no"]
    finally:
        # Delete the created events
        db_cursor.execute(
            "DELETE FROM CalendarEvent WHERE event_no = %s", (event["event_no"],)
        )
        db.commit()

        db_cursor.execute(
            "DELETE FROM CalendarEvent WHERE event_no = %s", (event2["event_no"],)
        )
        db.commit()

        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (course["course_code"],)
        )
        db.commit()

        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (course2["course_code"],)
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (lecturer["account_id"],)
        )
        db.commit()

        # Delete the student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (student["account_id"],)
        )
        db.commit()


def test_get_student_events():
    # Create a student
    student = AccountMocker.insert_mock_student()
    student_token = utils.create_student_token_from_mock(
        (student["mock_account"], student["mock_details"])
    )

    # Create a lecturer
    lecturer = AccountMocker.insert_mock_lecturer()

    # Create courses
    course = CourseMocker.insert_mock_course(lecturer)
    course2 = CourseMocker.insert_mock_course(lecturer)

    # Enrol student to the courses
    CourseMocker.enrol_mock_student(course, student)
    CourseMocker.enrol_mock_student(course2, student)

    # Create calendar events
    event = CalendarMocker.insert_event(course)
    event2 = CalendarMocker.insert_event(course2)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Get the created event
        response = test_client.get(
            f"/calendar/student/{student['student_id']}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={},
        )
        assert response.status_code == 200

        events = response.get_json()
        assert events
        assert len(events) == 2
        assert events[0]["event_name"] == event["event_name"]
        assert events[0]["event_no"] == event["event_no"]
        assert events[1]["event_name"] == event2["event_name"]
        assert events[1]["event_no"] == event2["event_no"]
    finally:
        # Delete the created events
        db_cursor.execute(
            "DELETE FROM CalendarEvent WHERE event_no = %s", (event["event_no"],)
        )
        db.commit()

        db_cursor.execute(
            "DELETE FROM CalendarEvent WHERE event_no = %s", (event2["event_no"],)
        )
        db.commit()

        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (course["course_code"],)
        )
        db.commit()

        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (course2["course_code"],)
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (lecturer["account_id"],)
        )
        db.commit()

        # Delete the student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (student["account_id"],)
        )
        db.commit()
