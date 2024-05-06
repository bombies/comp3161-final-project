from app import app
from modules.utils.db import db
from tests import utils
from tests.mockers.account_mocker import AccountMocker

test_client = app.test_client()
account_mocker = AccountMocker()
admin_token = utils.create_admin_token()


def test_registration():
    db_cursor = db.cursor(dictionary=True)
    mock_account = account_mocker.mock_account()

    body = {
        "email": mock_account["email"],
        "name": mock_account["name"],
        "account_type": mock_account["account_type"],
    }

    if mock_account["account_type"] == "Student":
        body["major"] = "Computer Science"
    else:
        body["department"] = "Computing"

    try:
        response = test_client.post(
            "/auth/register",
            headers={"Authorization": "Bearer " + admin_token},
            json=body,
        )

        assert response.status_code == 201

        response_json = utils.response_json(response)

        assert "id" in response_json
        assert "password" in response_json
        assert "token" in response_json
    finally:
        # Delete the user
        db_cursor.execute(
            "DELETE FROM Account WHERE email = %s", (mock_account["email"],)
        )
        db.commit()


def test_login():
    db_cursor = db.cursor(dictionary=True)
    mock_student = account_mocker.insert_mock_student()

    body = {
        "user_id": mock_student["mock_account"]["email"],
        "password": mock_student["mock_account"]["password"],
    }

    try:
        response = test_client.post("/auth/login", json=body)

        assert response.status_code == 200

        response_json = utils.response_json(response)

        assert "token" in response_json
    finally:
        # Delete the user
        db_cursor.execute(
            "DELETE FROM Account WHERE email = %s",
            (mock_student["mock_account"]["email"],),
        )
        db.commit()
