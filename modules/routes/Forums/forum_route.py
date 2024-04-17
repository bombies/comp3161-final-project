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

@app.route("/forums/course/<string:course_code>", methods=["GET"])
def get_course_forums(course_code):
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM DiscussionForum WHERE course_code = %s", (course_code,))
    forums = db_cursor.fetchall()
    if not forums:
        return jsonify({"message": "No forums found for this course"}), 404
    # Convert the forums data into JSON format and return
    return jsonify(forums), 200

@app.route("/forums/course/<string:course_code>", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer])
def create_course_forum(course_code):
    body = ForumSchema().load(request.get_json(force=True))
    body["course_code"] = course_code  # Set the course_code from the URL parameter

    db_cursor = db.cursor()
    try:
        db_cursor.execute(
            "INSERT INTO DiscussionForum (topic, post_time, creator, course_code) VALUES (%s, %s, %s, %s)",
            (body["topic"], body["post_time"], body["creator"], body["course_code"]),
        )
        db.commit()
        return jsonify({"message": "Forum created successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to create forum: {str(e)}"}), 500

@app.route("/threads/forum/<int:forum_id>", methods=["GET"])
def get_forum_threads(forum_id):
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM DiscussionThread WHERE forum_id = %s", (forum_id,))
    threads = db_cursor.fetchall()
    if not threads:
        return jsonify({"message": "No discussion threads found for this forum"}), 404
    # Convert the threads data into JSON format and return
    return jsonify(threads), 200

@app.route("/threads/forum/<int:forum_id>", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer, AccountType.Student])
def add_thread_to_forum(forum_id):
    body = NewDiscussionThreadSchema().load(request.get_json(force=True))
    # Assuming user_id is obtained from JWT token
    user_id = get_user_id_from_token(request.headers.get("Authorization"))

    db_cursor = db.cursor()
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


@app.route("/replies/thread/<int:thread_id>", methods=["POST"])
@protected_route(roles=[AccountType.Admin, AccountType.Lecturer, AccountType.Student])
def add_reply_to_thread(thread_id):
    body = NewDiscussionReplySchema().load(request.get_json(force=True))
    # Assuming user_id is obtained from JWT token
    user_id = get_user_id_from_token(request.headers.get("Authorization"))

    db_cursor = db.cursor()
    try:
        db_cursor.execute(
            "INSERT INTO DiscussionReply (thread_id, user_id, reply_text) VALUES (%s, %s, %s)",
            (thread_id, user_id, body["reply_text"]),
        )
        db.commit()
        return jsonify({"message": "Reply added successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to add reply: {str(e)}"}), 500

