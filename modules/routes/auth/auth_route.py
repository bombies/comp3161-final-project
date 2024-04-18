from flask import request, jsonify
from app import app
from marshmallow import Schema, fields, validate
from modules.models.account import AccountType
from modules.utils.db import db
from bcrypt import hashpw, gensalt, checkpw
from secrets import token_urlsafe
import jwt

from modules.utils.route_utils import handle_route, protected_route
from modules.utils.schema_utils import UnionField


class RegisterSchema(Schema):
    email = fields.Str(required=True)
    name = fields.Str(required=True)
    contact_info = fields.Str(required=False)
    account_type = fields.Str(
        validate=validate.OneOf([AccountType.Student.name, AccountType.Lecturer.name]),
        required=True,
    )

    # Student specific fields
    major = fields.Str(required=False)

    # Lecturer specific fields
    department = fields.Str(required=False)


class LoginSchema(Schema):
    user_id = UnionField(types=[str, int], required=True)
    password = fields.String(required=True)


@app.route("/auth/register", methods=["POST"])
@protected_route(roles=[AccountType.Admin])
def register():
    body = RegisterSchema().load(request.get_json(force=True))
    db_cursor = db.cursor()

    # Find if the email already exists.
    db_cursor.execute("SELECT * FROM Account WHERE email = %s", (body["email"],))
    if db_cursor.fetchone():
        return (
            jsonify({"message": "There is already a user with that email!"}),
            400,
        )

    major = body.get("major")
    dept = body.get("department")

    # Check if the major or department is provided based on the account type
    if body["account_type"] == AccountType.Student.name and not major:
        return (
            jsonify({"message": "Major is required for student accounts!"}),
            400,
        )
    elif body["account_type"] == AccountType.Lecturer.name and not dept:
        return (
            jsonify({"message": "Department is required for lecturer accounts!"}),
            400,
        )

    # Create the user, a JWT token and return the token to the user
    password = token_urlsafe(6)

    db_cursor.execute(
        "INSERT INTO Account (email, password, name, contact_info, account_type) VALUES (%s, %s, %s, %s, %s)",
        (
            body["email"],
            hash_password(password),
            body["name"],
            body.get("contact_info"),
            AccountType.Student.name,
        ),
    )

    db.commit()
    user_id = db_cursor.lastrowid

    # Based on the account type, create either a StudentDetails or LecturerDetails record
    if body["account_type"] == AccountType.Student.name:
        db_cursor.execute(
            "INSERT INTO StudentDetails (account_id, major) VALUES (%s, %s)",
            (user_id, major),
        )
    else:
        db_cursor.execute(
            "INSERT INTO LecturerDetails (account_id, department) VALUES (%s, %s)",
            (user_id, dept),
        )

    db.commit()

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
        jsonify({"id": user_id, "password": password, "token": token}),
        201,
    )


@app.route("/auth/login", methods=["POST"])
def login():
    def handler():
        body = LoginSchema().load(request.get_json(force=True))
        db_cursor = db.cursor()

        # Find user with the ID
        query = ""

        # If the user_id is an integer, search by account_id
        if (
            type(body["user_id"]) is int
            or type(body["user_id"]) is str
            and body["user_id"].isdigit()
        ):
            query = "account_id = %s"
        else:
            query = "email = %s"

        db_cursor.execute(
            f"SELECT * FROM Account WHERE {query}",
            (body["user_id"],),
        )
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
            jsonify({"token": token}),
            200,
        )

    return handle_route(handler=handler)


def hash_password(password: str):
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")
