from flask import request, jsonify
from app import app
from modules.models.account import AccountType
from modules.routes.Forums.forum_schema import (
    ForumSchema,
    DiscussionThreadSchema,
    DiscussionReplySchema,
    NewDiscussionThreadSchema,
    NewDiscussionReplySchema,

)
from modules.utils.db import db
from modules.utils.route_utils import authenticate, fetch_session, protected_route
from datetime import date

@app.route("/forums/course/<string:course_code>", methods=["GET", "POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer])
def handle_course_forums(course_code):
    if request.method == "GET":
        # Original logic to retrieve forums for the course
        db_cursor = db.cursor()
        db_cursor.execute("SELECT * FROM DiscussionForum WHERE course_code = %s", (course_code,))
        forums = db_cursor.fetchall()
        if not forums:
            return jsonify({"message": "No forums found for this course"}), 404
        # Convert the forums data into JSON format and return
        return jsonify(forums), 200
    elif request.method == "POST":
        # Additional logic for creating a forum for the course
        return create_course_forum(course_code)

from modules.utils.auth_utils import fetch_session

@app.route("/forums/course/<string:course_code>", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer])
def create_course_forum(course_code):
    # Check if the user is a student
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)
    if session["account_type"] == AccountType.Student.name:
        return jsonify({"message": "Students are not allowed to create forums"}), 403

    # Check if the user is a lecturer who teaches this course
    if session["account_type"] == AccountType.Lecturer.name:
        # Check if the lecturer teaches the specified course
        lecture_details = db_cursor.execute(
            "SELECT * FROM LecturerDetails WHERE account_id = %s", (session["sub"],)
        ).fetchone()
        if lecturer_id != lecture_details["lecturer_id"]:
            return jsonify({"message": "You can only view your own courses!"}), 403


    # Proceed with forum creation logic
    body = ForumSchema().load(request.get_json(force=True))
    body["course_code"] = course_code  

    db_cursor = db.cursor()
    try:
        db_cursor.execute(
            "INSERT INTO DiscussionForum (topic, post_time, creator, course_code) VALUES (%s, %s, %s, %s)",
            (body["topic"], date.today(), fetch_session()["sub"], body["course_code"]),
        )
        db.commit()
        return jsonify({"message": "Forum created successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to create forum: {str(e)}"}), 500


@app.route("/threads/forum/<int:forum_id>", methods=["GET", "POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer])
def handle_forum_threads(forum_id):
    # Check if the user is a student
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)
    if session["account_type"] == AccountType.Student.name:
        return jsonify({"message": "Students are not allowed to create forums"}), 403

    # Check if the user is a lecturer who teaches this course
    if session["account_type"] == AccountType.Lecturer.name:
        # Check if the lecturer teaches the specified course
        lecture_details = db_cursor.execute(
            "SELECT * FROM LecturerDetails WHERE account_id = %s", (session["sub"],)
        ).fetchone()
        if lecturer_id != lecture_details["lecturer_id"]:
            return jsonify({"message": "You can only view your own courses!"}), 403

    # Proceed with retrieving discussion threads for the forum
    db_cursor.execute("SELECT * FROM DiscussionThread WHERE forum_id = %s", (forum_id,))
    threads = db_cursor.fetchall()
    if not threads:
        return jsonify({"message": "No discussion threads found for this forum"}), 404
    # Convert the threads data into JSON format and return
    return jsonify(threads), 200

@app.route("/threads/forum/<int:forum_id>", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer, AccountType.Student])
def add_thread_to_forum(forum_id):
    # Check if the user is a student
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)
    if session["account_type"] == AccountType.Student.name:
        return jsonify({"message": "Students are not allowed to create forums"}), 403

    # Check if the user is a lecturer who teaches this course
    if session["account_type"] == AccountType.Lecturer.name:
        # Check if the lecturer teaches the specified course
        lecture_details = db_cursor.execute(
            "SELECT * FROM LecturerDetails WHERE account_id = %s", (session["sub"],)
        ).fetchone()
        if lecturer_id != lecture_details["lecturer_id"]:
            return jsonify({"message": "You can only view your own courses!"}), 403

    # Proceed with adding the discussion thread to the forum
    body = NewDiscussionThreadSchema().load(request.get_json(force=True))
    user_id = session["user_id"]  # Assuming user_id is obtained from JWT token

    try:
        db_cursor.execute(
            "INSERT INTO DiscussionThread (title, post, forum_id, user_id) VALUES (%s, %s, %s, %s)",
            (body["title"], body["post"], forum_id, user_id),
        )
        db.commit()
        return jsonify({"message": "Discussion thread added successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to add discussion thread: {str(e)}"}), 500


@app.route("/thread/<int:thread_id>/reply", methods=["POST"])
@protected_route()
def add_reply_to_thread(thread_id):
    body = NewDiscussionReplySchema().load(request.get_json(force=True))
    user_id = fetch_session()["sub"]

    db_cursor = db.cursor()
    try:
        db_cursor.execute(
            "INSERT INTO DiscussionReply (thread_id, user_id, reply_text, reply_time) VALUES (%s, %s, %s, %s)",
            (thread_id, user_id, body["reply_text"], date.today()),
        )
        db.commit()
        return jsonify({"message": "Reply added successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to add reply: {str(e)}"}), 500

