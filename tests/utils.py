from modules.models.account import AccountType
from tests.mockers.account_mocker import (
    AccountMocker,
    MockAccount,
    MockLecturerDetails,
    MockStudentDetails,
)
from flask import Response
import jwt
import os

account_mocker = AccountMocker()


def create_token(fields):
    return jwt.encode(
        payload={
            **fields,
        },
        key=os.getenv("JWT_SECRET"),
        algorithm="HS256",
    )


def create_admin_token(id=1):
    return create_token(
        {
            "sub": id,
            "name": "Admin",
            "email": "admin@email.com",
            "account_type": AccountType.Admin.name,
        }
    )


def create_student_token_from_mock(
    student_mock: tuple[MockAccount, MockStudentDetails]
):
    account, details = student_mock
    return create_token(
        {
            "sub": details["account_id"],
            "name": account["name"],
            "email": account["email"],
            "account_type": AccountType.Student.name,
        }
    )


def create_lecturer_token_from_mock(
    lecturer_mock: tuple[MockAccount, MockLecturerDetails]
):
    account, details = lecturer_mock
    return create_token(
        {
            "sub": details["account_id"],
            "name": account["name"],
            "email": account["email"],
            "account_type": AccountType.Lecturer.name,
        }
    )


def response_json(response: Response):
    return response.get_json(force=True)
