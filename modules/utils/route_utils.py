from functools import wraps
from json import JSONDecodeError
from traceback import print_exception
from flask import jsonify, request
from marshmallow import ValidationError
from app import app
import jwt

from modules.models.account import AccountType


def handle_route(handler):
    try:
        return handler()
    except ValidationError as e:
        return jsonify(e.messages), 400
    except JSONDecodeError as e:
        return jsonify({"message": "Invalid JSON body"}), 400
    except Exception as e:
        print_exception(e)
        return (
            jsonify({"message": "Something went wrong!"}),
            500,
        )


def protected_route(roles: list[AccountType] = []):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            auth_result = authenticate(roles)
            if auth_result:
                return auth_result

            return handle_route(lambda: f(*args, **kwargs))

        return wrapped

    return decorator


def authenticate(roles: list[AccountType]):
    if not request:
        return (
            jsonify(
                {
                    "message": "The authenticate function can't be used because it isn't in an endpoint function!"
                }
            ),
            500,
        )

    session = fetch_session()
    if not session:
        return jsonify({"message": "Unauthorized"}), 401

    if len(roles) != 0 and AccountType[session["account_type"]] not in roles:
        return jsonify({"message": "Unauthorized"}), 401

    return None


def fetch_session():
    if not app or not request:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        directive, token = auth_header.split(" ")
        if directive != "Bearer":
            return None

        decoded_token = jwt.decode(
            token, app.config["JWT_SECRET"], algorithms=["HS256"]
        )
        return decoded_token
    except jwt.DecodeError:
        return None
    except ValueError:
        return None
