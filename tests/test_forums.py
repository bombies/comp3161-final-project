from app import app
from tests.mockers.forum_mocker import ForumMocker
from tests.mockers.account_mocker import AccountMocker
from tests.mockers.course_mocker import CourseMocker
from modules.utils.db import db
import tests.utils as utils

test_client = app.test_client()
forum_mocker = ForumMocker()
account_mocker = AccountMocker()
course_mocker = CourseMocker()
admin_token = utils.create_admin_token()


def test_forum_creation():
    # Create lecturer
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    lecturer_token = utils.create_lecturer_token_from_mock(
        (
            mock_lecturer["mock_account"],
            mock_lecturer["mock_details"],
        )
    )

    # Create a course
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Create a forum for the course
        response = test_client.post(
            f"/course/{mock_course['course_code']}/forums",
            headers={"Authorization": f"Bearer {lecturer_token}"},
            json={"topic": "General Discussion"},
        )
        assert response.status_code == 201

        forum = response.get_json()
        assert forum["topic"] == "General Discussion"
        assert forum["course_code"] == mock_course["course_code"]

        # Delete forum
        db_cursor.execute(
            "DELETE FROM DiscussionForum WHERE forum_id = %s", (forum["forum_id"],)
        )
        db.commit()
    finally:
        # Delete course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (mock_course["course_code"],)
        )
        db.commit()

        # Delete lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_forums_fetch():
    # Create lecturer
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    lecturer_token = utils.create_lecturer_token_from_mock(
        (
            mock_lecturer["mock_account"],
            mock_lecturer["mock_details"],
        )
    )

    # Create a course
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create forum
    forum = ForumMocker.insert_mock_forum(mock_lecturer, mock_course)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Fetch the forum
        response = test_client.get(
            f"/course/{mock_course['course_code']}/forums",
            headers={"Authorization": f"Bearer {lecturer_token}"},
        )
        assert response.status_code == 200

        fetched_forums = response.get_json()
        assert len(fetched_forums) == 1

        fetched_forum = fetched_forums[0]
        assert fetched_forum["forum_id"] == forum["forum_id"]
        assert fetched_forum["topic"] == forum["topic"]
        assert fetched_forum["course_code"] == mock_course["course_code"]
    finally:
        # Delete forum
        db_cursor.execute(
            "DELETE FROM DiscussionForum WHERE forum_id = %s", (forum["forum_id"],)
        )
        db.commit()

        # Delete course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (mock_course["course_code"],)
        )
        db.commit()

        # Delete lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_thread_creation():
    # Create lecturer
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    lecturer_token = utils.create_lecturer_token_from_mock(
        (
            mock_lecturer["mock_account"],
            mock_lecturer["mock_details"],
        )
    )

    # Create a course
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create forum
    forum = ForumMocker.insert_mock_forum(mock_lecturer, mock_course)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Create a thread in the forum
        response = test_client.post(
            f"course/{mock_course['course_code']}/forums/{forum['forum_id']}/threads",
            headers={"Authorization": f"Bearer {lecturer_token}"},
            json={"title": "Hello World", "post": "This is a test thread"},
        )
        assert response.status_code == 201

        thread = response.get_json()
        assert thread["forum_id"] == forum["forum_id"]

        # Delete thread
        db_cursor.execute(
            "DELETE FROM DiscussionThread WHERE thread_id = %s", (thread["thread_id"],)
        )
        db.commit()
    finally:
        # Delete forum
        db_cursor.execute(
            "DELETE FROM DiscussionForum WHERE forum_id = %s", (forum["forum_id"],)
        )
        db.commit()

        # Delete course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (mock_course["course_code"],)
        )
        db.commit()

        # Delete lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_thread_fetch():
    # Create lecturer
    mock_lecturer = AccountMocker.insert_mock_lecturer()
    lecturer_token = utils.create_lecturer_token_from_mock(
        (
            mock_lecturer["mock_account"],
            mock_lecturer["mock_details"],
        )
    )

    # Create a course
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create forum
    forum = ForumMocker.insert_mock_forum(mock_lecturer, mock_course)

    # Create thread
    thread = ForumMocker.insert_mock_discussion_thread(forum)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Fetch the thread
        response = test_client.get(
            f"/course/{mock_course['course_code']}/forums/{forum['forum_id']}/threads",
            headers={"Authorization": f"Bearer {lecturer_token}"},
        )
        assert response.status_code == 200

        fetched_threads = response.get_json()
        assert len(fetched_threads) == 1

        fetched_thread = fetched_threads[0]
        assert fetched_thread["thread_id"] == thread["thread_id"]
        assert fetched_thread["forum_id"] == forum["forum_id"]
    finally:
        # Delete thread
        db_cursor.execute(
            "DELETE FROM DiscussionThread WHERE thread_id = %s", (thread["thread_id"],)
        )
        db.commit()

        # Delete forum
        db_cursor.execute(
            "DELETE FROM DiscussionForum WHERE forum_id = %s", (forum["forum_id"],)
        )
        db.commit()

        # Delete course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (mock_course["course_code"],)
        )
        db.commit()

        # Delete lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()


def test_thread_reply():
    # Create lecturer
    mock_lecturer = AccountMocker.insert_mock_lecturer()

    # Create a course
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create forum
    forum = ForumMocker.insert_mock_forum(mock_lecturer, mock_course)

    # Create thread
    thread = ForumMocker.insert_mock_discussion_thread(forum)

    # Create student
    mock_student = AccountMocker.insert_mock_student()
    student_token = utils.create_student_token_from_mock(
        (
            mock_student["mock_account"],
            mock_student["mock_details"],
        )
    )

    # Enrol student
    CourseMocker.enrol_mock_student(mock_course, mock_student)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Create a reply to the thread
        response = test_client.post(
            f"/course/{mock_course['course_code']}/forums/{forum['forum_id']}/threads/{thread['thread_id']}/reply",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"reply_text": "This is a test reply"},
        )
        assert response.status_code == 201

        reply = response.get_json()
        assert reply["thread_id"] == thread["thread_id"]
        assert reply["reply_text"] == "This is a test reply"

        # Delete reply
        db_cursor.execute(
            "DELETE FROM DiscussionReply WHERE reply_id = %s", (reply["reply_id"],)
        )
        db.commit()
    finally:
        # Delete thread
        db_cursor.execute(
            "DELETE FROM DiscussionThread WHERE thread_id = %s", (thread["thread_id"],)
        )
        db.commit()

        # Delete forum
        db_cursor.execute(
            "DELETE FROM DiscussionForum WHERE forum_id = %s", (forum["forum_id"],)
        )
        db.commit()

        # Delete course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (mock_course["course_code"],)
        )
        db.commit()

        # Delete student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_student["account_id"],)
        )
        db.commit()

        # Delete lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )


def test_fetch_replies():
    # Create lecturer
    mock_lecturer = AccountMocker.insert_mock_lecturer()

    # Create a course
    mock_course = CourseMocker.insert_mock_course(mock_lecturer)

    # Create forum
    forum = ForumMocker.insert_mock_forum(mock_lecturer, mock_course)

    # Create thread
    thread = ForumMocker.insert_mock_discussion_thread(forum)

    # Create student
    mock_student = AccountMocker.insert_mock_student()
    student_token = utils.create_student_token_from_mock(
        (
            mock_student["mock_account"],
            mock_student["mock_details"],
        )
    )

    # Enrol student
    CourseMocker.enrol_mock_student(mock_course, mock_student)

    # Create reply
    reply = ForumMocker.insert_mock_discussion_reply(thread, mock_student)

    db_cursor = db.cursor(dictionary=True)

    try:
        # Fetch the replies
        response = test_client.get(
            f"/course/{mock_course['course_code']}/forums/{forum['forum_id']}/threads/{thread['thread_id']}/replies",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == 200

        fetched_replies = response.get_json()
        assert len(fetched_replies) == 1

        fetched_reply = fetched_replies[0]
        assert fetched_reply["reply_id"] == reply["reply_id"]
        assert fetched_reply["thread_id"] == thread["thread_id"]
    finally:
        # Delete reply
        db_cursor.execute(
            "DELETE FROM DiscussionReply WHERE reply_id = %s", (reply["reply_id"],)
        )
        db.commit()

        # Delete thread
        db_cursor.execute(
            "DELETE FROM DiscussionThread WHERE thread_id = %s", (thread["thread_id"],)
        )
        db.commit()

        # Delete forum
        db_cursor.execute(
            "DELETE FROM DiscussionForum WHERE forum_id = %s", (forum["forum_id"],)
        )
        db.commit()

        # Delete course
        db_cursor.execute(
            "DELETE FROM Course WHERE course_code = %s", (mock_course["course_code"],)
        )
        db.commit()

        # Delete student
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_student["account_id"],)
        )
        db.commit()

        # Delete lecturer
        db_cursor.execute(
            "DELETE FROM Account WHERE account_id = %s", (mock_lecturer["account_id"],)
        )
        db.commit()
