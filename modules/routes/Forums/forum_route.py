from flask import request, jsonify
from app import app
from modules.models.account import AccountType
from modules.routes.courses.courses_route import (
    _check_course_visibility,
)
from modules.routes.forums.forum_schema import (
    ForumSchema,
    NewDiscussionReplySchema,
)
from modules.utils.db import db
from modules.utils.route_utils import authenticate, fetch_session, protected_route
from datetime import date, datetime
import traceback


@app.route("/course/<string:course_code>/forums", methods=["GET", "POST"])
@protected_route()
def handle_course_forums(course_code):
    if request.method == "GET":
        return get_course_forums(course_code)
    elif request.method == "POST":
        return create_course_forum(course_code)


def get_course_forums(
    course_code, session=fetch_session(), db_cursor=db.cursor(dictionary=True)
):
    visibility_res = _check_course_visibility(
        session,
        course_code,
        err_msgs={
            "student_err": "You can only view forums for your courses!",
            "lecturer_err": "You can only view forums for your courses!",
        },
    )

    if visibility_res:
        return visibility_res

    # Original logic to retrieve forums for the course
    db_cursor.execute(
        "SELECT * FROM DiscussionForum WHERE course_code = %s", (course_code,)
    )
    forums = db_cursor.fetchall()
    if not forums:
        return jsonify({"message": "No forums found for this course"}), 404
    # Convert the forums data into JSON format and return
    return jsonify(forums), 200


def create_course_forum(course_code):
    auth_res = authenticate([AccountType.Lecturer, AccountType.Admin])
    if auth_res:
        return auth_res

    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    if session["account_type"] == AccountType.Student.name:
        return jsonify({"message": "Students are not allowed to create forums"}), 403

    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only create forums for your own courses!",
        },
    )

    if visibility_res:
        return visibility_res

    # Proceed with forum creation logic
    body = ForumSchema().load(request.get_json(force=True))

    db_cursor = db.cursor(dictionary=True)
    try:
        db_cursor.execute(
            "INSERT INTO DiscussionForum (topic, post_time, creator, course_code) VALUES (%s, %s, %s, %s)",
            (body["topic"], date.today(), fetch_session()["sub"], course_code),
        )
        db.commit()

        created_forum_id = db_cursor.lastrowid
        db_cursor.execute(
            "SELECT * FROM DiscussionForum WHERE forum_id = %s", (created_forum_id,)
        )

        created_forum = db_cursor.fetchone()
        return jsonify(created_forum), 201
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return jsonify({"message": f"Failed to create forum: {str(e)}"}), 500


@app.route(
    "/course/<string:course_code>/forums/<int:forum_id>/threads",
    methods=["GET", "POST"],
)
@protected_route()
def handle_forum_threads(course_code: str, forum_id: int):
    if request.method == "GET":
        return get_forum_threads(forum_id, course_code)
    elif request.method == "POST":
        return add_thread_to_forum(forum_id, course_code)


def get_forum_threads(forum_id: int, course_code: str):
    # Check if the user is a student
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)
    if session["account_type"] == AccountType.Student.name:
        return jsonify({"message": "Students are not allowed to create forums"}), 403

    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only view your own courses!",
        },
    )

    if visibility_res:
        return visibility_res

    # Proceed with retrieving discussion threads for the forum
    db_cursor.execute("SELECT * FROM DiscussionThread WHERE forum_id = %s", (forum_id,))
    threads = db_cursor.fetchall()
    if not threads:
        return jsonify({"message": "No discussion threads found for this forum"}), 404
    # Convert the threads data into JSON format and return
    return jsonify(threads), 200


def add_thread_to_forum(forum_id: int, course_code: str):
    # Check if the user is a student
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)
    if session["account_type"] == AccountType.Student.name:
        return jsonify({"message": "Students are not allowed to create forums"}), 403

    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only view your own courses!",
        },
    )

    if visibility_res:
        return visibility_res

    try:
        db_cursor.execute(
            "INSERT INTO DiscussionThread (replies, timeStamp, forum_id) VALUES (%s, %s, %s)",
            (0, datetime.now(), forum_id),
        )
        db.commit()

        thread_id = db_cursor.lastrowid
        db_cursor.execute(
            "SELECT * FROM DiscussionThread WHERE thread_id = %s", (thread_id,)
        )

        thread = db_cursor.fetchone()
        return jsonify(thread), 201
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return jsonify({"message": f"Failed to add discussion thread: {str(e)}"}), 500


@app.route(
    "/course/<string:course_code>/forums/<int:forum_id>/threads/<int:thread_id>/reply",
    methods=["POST"],
)
@protected_route()
def add_reply_to_thread(course_code: str, forum_id: int, thread_id: int):
    db_cursor = db.cursor(dictionary=True)
    body = NewDiscussionReplySchema().load(request.get_json(force=True))
    user_id = fetch_session()["sub"]

    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only make replies to threads in courses that you lecture!",
            "student_err": "You are not enrolled in this course!",
        },
    )

    if visibility_res:
        return visibility_res

    try:
        db_cursor.execute(
            "INSERT INTO DiscussionReply (thread_id, user_id, reply_text, reply_time) VALUES (%s, %s, %s, %s)",
            (thread_id, user_id, body["reply_text"], date.today()),
        )
        db.commit()

        reply_id = db_cursor.lastrowid
        db_cursor.execute(
            "SELECT * FROM DiscussionReply WHERE reply_id = %s", (reply_id,)
        )

        reply = db_cursor.fetchone()
        return jsonify(reply), 201
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return jsonify({"message": f"Failed to add reply: {str(e)}"}), 500


@app.route(
    "/course/<string:course_code>/forums/<int:forum_id>/threads/<int:thread_id>/replies",
    methods=["GET"],
)
@protected_route()
def get_replies(course_code: str, forum_id: int, thread_id: int):
    db_cursor = db.cursor(dictionary=True)

    # Check if the user is a lecturer who teaches this course
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "lecturer_err": "You can only view your own courses!",
            "student_err": "You are not enrolled in this course!",
        },
    )

    if visibility_res:
        return visibility_res

    # Proceed with retrieving discussion replies for the thread
    db_cursor.execute(
        "SELECT * FROM DiscussionReply WHERE thread_id = %s", (thread_id,)
    )
    replies = db_cursor.fetchall()
    if not replies:
        return jsonify({"message": "No discussion replies found for this thread"}), 404
    # Convert the replies data into JSON format and return
    return jsonify(replies), 200
