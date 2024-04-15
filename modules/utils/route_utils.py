from json import JSONDecodeError
from traceback import print_exception
from flask import jsonify
from marshmallow import ValidationError


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
