from flask import request, jsonify
from app import app
from marshmallow import Schema, fields
from modules.models.account import AccountType
from modules.utils.db import db
from bcrypt import hashpw, gensalt, checkpw
import jwt

from modules.utils.route_utils import handle_route


class RegisterSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    name = fields.String(required=True)
    contact_info = fields.String(required=False)


class LoginSchema(Schema):
    user_id = fields.Int(required=True)
    password = fields.String(required=True)


@app.route("/auth/register", methods=["POST"])
def register():
    def handler():
        body = RegisterSchema().load(request.get_json(force=True))
        db_cursor = db.cursor()

        # Find if the email already exists.
        db_cursor.execute("SELECT * FROM Account WHERE email = %s", (body["email"],))
        if db_cursor.fetchone():
            return (
                jsonify({"message": "There is already a user with that email!"}),
                400,
            )

        # Create the user, a JWT token and return the token to the user
        db_cursor.execute(
            "INSERT INTO Account (email, password, name, contact_info, account_type) VALUES (%s, %s, %s, %s, %s)",
            (
                body["email"],
                hashpw(body["password"].encode("utf-8"), gensalt()).decode("utf-8"),
                body["name"],
                body.get("contact_info"),
                AccountType.Student.name,
            ),
        )

        db.commit()
        user_id = db_cursor.lastrowid

        token = jwt.encode(
            payload={
                "sub": user_id,
                "name": body["name"],
                "email": body["email"],
                "account_type": AccountType.Student.name,
            },
            key=app.config["JWT_SECRET"],
            algorithm="HS256",
        )
        return (
            jsonify(
                {
                    "message": "User created successfully!",
                    "data": {"id": user_id, "token": token},
                }
            ),
            201,
        )

    return handle_route(handler=handler)


@app.route("/auth/login", methods=["POST"])
def login():
    def handler():
        body = LoginSchema().load(request.get_json(force=True))
        db_cursor = db.cursor()

        # Find user with the ID
        db_cursor.execute("SELECT * FROM Account WHERE email = %s", (body["user_id"],))
        user = db_cursor.fetchone()

        # If the user does not exist, return an error.
        if not user:
            return (
                jsonify({"message": "Invalid credentails!"}),
                400,
            )

        # If the password is incorrect, return an error.
        if not checkpw(body["password"].encode("utf-8"), user[2].encode("utf-8")):
            return (
                jsonify({"message": "Invalid credentails!"}),
                400,
            )

        # Create a JWT token and return the token to the user
        token = jwt.encode(
            payload={
                "sub": user[0],
                "name": user[5],
                "email": user[1],
                "account_type": user[3],
            },
            key=app.config["JWT_SECRET"],
            algorithm="HS256",
        )

        return (
            jsonify(
                {
                    "message": "User logged in successfully!",
                    "data": {"token": token},
                }
            ),
            200,
        )

    return handle_route(handler=handler)
