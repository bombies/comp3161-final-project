from typing import TypedDict
from faker import Faker

from modules.routes.auth.auth_route import hash_password
from modules.utils.db import db


class MockAccount(TypedDict):
    account_id: int
    name: str
    email: str
    password: str
    account_type: str


class MockLecturerDetails(TypedDict):
    department: str
    lecturer_id: int
    account_id: int


class MockStudentDetails(TypedDict):
    major: str
    student_id: int
    account_id: int


class LecturerMockInsertionResult(TypedDict):
    mock_account: MockAccount
    mock_details: MockLecturerDetails
    account_id: int
    lecturer_id: int


class StudentMockInsertionResult(TypedDict):
    mock_account: MockAccount
    mock_details: MockStudentDetails
    account_id: int
    student_id: int


class AccountMocker:
    def __init__(self):
        self.fake = Faker()

    def mock_account(self) -> MockAccount:
        return {
            "account_id": self.fake.random_int(),
            "name": self.fake.name(),
            "email": self.fake.email(),
            "password": self.fake.password(),
            "account_type": self.fake.random_element(["Student", "Lecturer"]),
        }

    def mock_student_account(self) -> tuple[MockAccount, MockStudentDetails]:
        mock_account = self.mock_account()
        mock_account["account_type"] = "Student"

        mock_student_details = {
            "major": self.fake.random_element(
                ["Computer Science", "Mathematics", "Physics"]
            ),
            "student_id": self.fake.random_int(),
            "account_id": mock_account["account_id"],
        }

        return mock_account, mock_student_details

    def mock_lecturer_account(self) -> tuple[MockAccount, MockLecturerDetails]:
        mock_account = self.mock_account()
        mock_account["account_type"] = "Lecturer"

        mock_lecturer_details = {
            "department": self.fake.random_element(
                ["Computer Science", "Mathematics", "Physics"]
            ),
            "lecturer_id": self.fake.random_int(),
            "account_id": mock_account["account_id"],
        }

        return mock_account, mock_lecturer_details

    @staticmethod
    def insert_mock_lecturer() -> LecturerMockInsertionResult:
        # Insert mock lecturer account to database
        account_mocker = AccountMocker()
        lecturer_account, lecturer_details = account_mocker.mock_lecturer_account()
        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute(
            "INSERT INTO Account (email, password, name, account_type) VALUES (%s, %s, %s, %s)",
            (
                lecturer_account["email"],
                hash_password(lecturer_account["password"]),
                lecturer_account["name"],
                lecturer_account["account_type"],
            ),
        )
        db.commit()
        lecturer_account_id = db_cursor.lastrowid

        db_cursor.execute(
            "INSERT INTO LecturerDetails (account_id, department) VALUES (%s, %s)",
            (lecturer_account_id, lecturer_details["department"]),
        )
        db.commit()
        lecturer_id = db_cursor.lastrowid

        lecturer_account["account_id"] = lecturer_account_id
        lecturer_details["account_id"] = lecturer_account_id
        lecturer_details["lecturer_id"] = lecturer_id

        return {
            "mock_account": lecturer_account,
            "mock_details": lecturer_details,
            "account_id": lecturer_account_id,
            "lecturer_id": lecturer_id,
        }

    @staticmethod
    def insert_mock_student() -> StudentMockInsertionResult:
        # Insert mock student account to database
        account_mocker = AccountMocker()
        student_account, student_details = account_mocker.mock_student_account()
        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute(
            "INSERT INTO Account (email, password, name, account_type) VALUES (%s, %s, %s, %s)",
            (
                student_account["email"],
                hash_password(student_account["password"]),
                student_account["name"],
                student_account["account_type"],
            ),
        )
        db.commit()
        student_account_id = db_cursor.lastrowid

        db_cursor.execute(
            "INSERT INTO StudentDetails (account_id, major) VALUES (%s, %s)",
            (student_account_id, student_details["major"]),
        )
        db.commit()
        student_id = db_cursor.lastrowid

        student_account["account_id"] = student_account_id
        student_details["account_id"] = student_account_id
        student_details["student_id"] = student_id

        return {
            "mock_account": student_account,
            "mock_details": student_details,
            "account_id": student_account_id,
            "student_id": student_id,
        }
