from app import app
from tests.mockers.course_mocker import CourseMocker
import tests.utils as utils

from modules.utils.db import db
from tests.mockers.account_mocker import AccountMocker

test_client = app.test_client()
account_mocker = AccountMocker()
admin_token = utils.create_admin_token()


def test_course_creation():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    db_cursor = db.cursor(dictionary=True)

    try:
        response = test_client.post(
            "/courses",
            headers={"Authorization": "Bearer " + admin_token},
            json={
                "course_code": "CS101",
                "course_name": "Introduction to Computer Science",
                "lecturer_id": mock_lecturer["lecturer_id"],
                "semester": 1,
            },
        )

        response_json = utils.response_json(response)

        assert response.status_code == 201
        assert response_json["course_code"] != None

        course_code = response_json["course_code"]

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()
    finally:
        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_course_update():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)
    course_code = mock_course["course_code"]

    try:
        response = test_client.patch(
            f"/courses/{course_code}",
            headers={"Authorization": "Bearer " + admin_token},
            json={
                "course_name": "Introduction to Computer Science 2",
                "semester": 2,
            },
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert response_json["course_name"] == "Introduction to Computer Science 2"
        assert response_json["semester"] == 2

    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_courses_fetch():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    try:
        response = test_client.get(
            "/courses",
            headers={"Authorization": "Bearer " + admin_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert len(response_json) > 0
        assert response_json[0]["course_code"] == mock_course["course_code"]
        assert (
            response_json[0]["course_name"]
            == mock_course["course_details"]["course_name"]
        )
        assert response_json[0]["semester"] == mock_course["course_details"]["semester"]
        assert (
            response_json[0]["lecturer_id"]
            == mock_course["course_details"]["lecturer_id"]
        )

    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s",
            (mock_course["course_code"],),
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_course_fetch():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)
    course_code = mock_course["course_code"]

    try:
        response = test_client.get(
            f"/courses/{course_code}",
            headers={"Authorization": "Bearer " + admin_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert response_json["course_code"] == course_code
        assert (
            response_json["course_name"] == mock_course["course_details"]["course_name"]
        )
        assert response_json["semester"] == mock_course["course_details"]["semester"]
        assert (
            response_json["lecturer_id"] == mock_course["course_details"]["lecturer_id"]
        )

    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_course_registration():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_student = AccountMocker.insert_mock_student()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)
    course_code = mock_course["course_code"]
    student_jwt_token = utils.create_student_token_from_mock(
        (mock_student["mock_account"], mock_student["mock_details"])
    )

    try:
        response = test_client.post(
            f"/courses/register/{course_code}",
            headers={"Authorization": "Bearer " + student_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 201
        assert response_json["course_code"] == course_code
        assert response_json["student_id"] == mock_student["student_id"]
    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the enrolment
        db_cursor.execute(
            "DELETE FROM Enrollment WHERE course_code = %s AND student_id = %s",
            (course_code, mock_student["student_id"]),
        )
        db.commit()

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_student["account_id"],)
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_course_unregistration():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_student = AccountMocker.insert_mock_student()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)
    course_code = mock_course["course_code"]
    student_jwt_token = utils.create_student_token_from_mock(
        (mock_student["mock_account"], mock_student["mock_details"])
    )

    # Create enrolment entry in db
    CourseMocker.enrol_mock_student(mock_course, mock_student)

    try:
        response = test_client.delete(
            f"/courses/unregister/{course_code}",
            headers={"Authorization": "Bearer " + student_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert response_json["course_code"] == course_code
        assert response_json["student_id"] == mock_student["student_id"]
    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_student["account_id"],)
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_get_courses_for_student():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_student = AccountMocker.insert_mock_student()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create enrolment entry in db
    CourseMocker.enrol_mock_student(mock_course, mock_student)

    course_code = mock_course["course_code"]

    student_jwt_token = utils.create_student_token_from_mock(
        (mock_student["mock_account"], mock_student["mock_details"])
    )

    try:
        response = test_client.get(
            f"/courses/student/{mock_student['student_id']}",
            headers={"Authorization": "Bearer " + student_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert len(response_json) > 0
        assert response_json[0]["course_code"] == course_code
        assert (
            response_json[0]["course_name"]
            == mock_course["course_details"]["course_name"]
        )
        assert response_json[0]["semester"] == mock_course["course_details"]["semester"]
        assert (
            response_json[0]["lecturer_id"]
            == mock_course["course_details"]["lecturer_id"]
        )

    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the enrolment
        db_cursor.execute(
            "DELETE FROM Enrollment WHERE course_code = %s AND student_id = %s",
            (course_code, mock_student["student_id"]),
        )
        db.commit()

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_student["account_id"],)
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_get_courses_for_lecturer():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    course_code = mock_course["course_code"]

    lecturer_jwt_token = utils.create_lecturer_token_from_mock(
        (mock_lecturer["mock_account"], mock_lecturer["mock_details"])
    )

    try:
        response = test_client.get(
            f"/courses/lecturer/{mock_lecturer['lecturer_id']}",
            headers={"Authorization": "Bearer " + lecturer_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert len(response_json) > 0
        assert response_json[0]["course_code"] == course_code
        assert (
            response_json[0]["course_name"]
            == mock_course["course_details"]["course_name"]
        )
        assert response_json[0]["semester"] == mock_course["course_details"]["semester"]
        assert (
            response_json[0]["lecturer_id"]
            == mock_course["course_details"]["lecturer_id"]
        )

    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_get_course_members():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_student = AccountMocker.insert_mock_student()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create enrolment entry in db
    CourseMocker.enrol_mock_student(mock_course, mock_student)

    course_code = mock_course["course_code"]

    lecturer_jwt_token = utils.create_lecturer_token_from_mock(
        (mock_lecturer["mock_account"], mock_lecturer["mock_details"])
    )

    try:
        response = test_client.get(
            f"/courses/{course_code}/members",
            headers={"Authorization": "Bearer " + lecturer_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert len(response_json) > 0
        assert response_json[0]["student_id"] == mock_student["student_id"]
    finally:
        db_cursor = db.cursor(dictionary=True)

        # Delete the enrolment
        db_cursor.execute(
            "DELETE FROM Enrollment WHERE course_code = %s AND student_id = %s",
            (course_code, mock_student["student_id"]),
        )
        db.commit()

        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_student["account_id"],)
        )
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_assignment_creation():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)
    course_code = mock_course["course_code"]

    lecturer_jwt_token = utils.create_lecturer_token_from_mock(
        (mock_lecturer["mock_account"], mock_lecturer["mock_details"])
    )

    db_cursor = db.cursor(dictionary=True)

    try:
        response = test_client.post(
            f"/courses/{course_code}/assignments",
            headers={"Authorization": "Bearer " + lecturer_jwt_token},
            json={
                "title": "Assignment 1",
                "deadline": "2024-12-22T03:12:58.019077+00:00",
                "total_marks": 100.00,
            },
        )

        response_json = utils.response_json(response)

        try:
            assert response.status_code == 201
        except AssertionError as e:
            print("Error response: ", response_json)
            raise e

        assert response_json["assignment_id"] != None

        assignment_id = response_json["assignment_id"]

        # Delete the assignment
        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute(
            "DELETE FROM Assignment WHERE assignment_id = %s", (assignment_id,)
        )
        db.commit()
    finally:
        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_get_assigments():
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    mock_student = AccountMocker.insert_mock_student()
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)
    course_code = mock_course["course_code"]

    lecturer_jwt_token = utils.create_lecturer_token_from_mock(
        (mock_lecturer["mock_account"], mock_lecturer["mock_details"])
    )

    student_jwt_token = utils.create_student_token_from_mock(
        (mock_student["mock_account"], mock_student["mock_details"])
    )

    # Enrol student to course
    CourseMocker.enrol_mock_student(mock_course, mock_student)

    # Insert mock assignment
    mock_assignment = CourseMocker.insert_mock_assignment(mock_course)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Test as a lecturer
        response = test_client.get(
            f"/courses/{course_code}/assignments",
            headers={"Authorization": "Bearer " + lecturer_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert len(response_json) == 1

        # Test as an enrolled student
        response = test_client.get(
            f"/courses/{course_code}/assignments",
            headers={"Authorization": "Bearer " + student_jwt_token},
        )

        response_json = utils.response_json(response)

        assert response.status_code == 200
        assert len(response_json) > 0
        assert response_json[0]["assignment_id"] == mock_assignment["assignment_id"]
        assert response_json[0]["course_code"] == course_code
        assert response_json[0]["title"] == mock_assignment["title"]
        assert response_json[0]["description"] == mock_assignment["description"]
        # assert parse_date(response_json[0]["deadline"]).strftime(
        #     "%Y-%m-%dT%H:%M:%S.%f%z"
        # ) == mock_assignment["deadline"].strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        assert float(response_json[0]["total_marks"]) == mock_assignment["total_marks"]
    finally:
        # Delete the course
        db_cursor.execute("DELETE FROM Course WHERE course_code = %s", (course_code,))
        db.commit()

        # Delete the lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()
