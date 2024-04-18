import datetime
from typing import TypedDict
from faker import Faker

from modules.utils.db import db
from tests.mockers.account_mocker import (
    LecturerMockInsertionResult,
    StudentMockInsertionResult,
)


class MockCourse(TypedDict):
    course_code: str
    course_name: str
    semester: int
    lecturer_id: int


class MockAssignment(TypedDict):
    assignment_id: int
    course_code: str
    title: str
    description: str | None
    deadline: datetime
    total_marks: float


class CourseMockInsertionResult(TypedDict):
    course_details: MockCourse
    course_code: str


class CourseMocker:
    def __init__(self):
        self.fake = Faker()

    def mock_course(self) -> MockCourse:
        return {
            "course_code": self.fake.random_element(
                [
                    "CS101",
                    "CS102",
                    "CS103",
                    "CS104",
                    "CS105",
                    "CS106",
                    "CS107",
                    "CS108",
                    "CS109",
                    "CS110",
                    "CS111",
                    "CS112",
                    "CS113",
                    "CS114",
                    "CS115",
                    "CS116",
                    "CS117",
                    "CS118",
                    "CS119",
                    "CS120",
                ]
            ),
            "course_name": self.fake.random_element(
                [
                    "Introduction to Computer Science",
                    "Data Structures and Algorithms",
                    "Computer Networks",
                    "Operating Systems",
                    "Software Engineering",
                    "Database Management Systems",
                    "Web Development",
                    "Mobile Application Development",
                    "Artificial Intelligence",
                    "Machine Learning",
                    "Computer Vision",
                    "Natural Language Processing",
                    "Computer Graphics",
                    "Cybersecurity",
                    "Computer Architecture",
                    "Parallel Computing",
                    "Distributed Systems",
                    "Cloud Computing",
                    "Internet of Things",
                    "Blockchain Technology",
                ],
            ),
            "semester": self.fake.random_int(min=1, max=2),
            "lecturer_id": self.fake.random_int(),
        }

    def mock_assignment(self) -> MockAssignment:
        return {
            "assignment_id": self.fake.random_int(),
            "course_code": self.fake.random_element(
                [
                    "CS101",
                    "CS102",
                    "CS103",
                    "CS104",
                    "CS105",
                    "CS106",
                    "CS107",
                    "CS108",
                    "CS109",
                    "CS110",
                    "CS111",
                    "CS112",
                    "CS113",
                    "CS114",
                    "CS115",
                    "CS116",
                    "CS117",
                    "CS118",
                    "CS119",
                    "CS120",
                ]
            ),
            "title": self.fake.random_element(
                [
                    "Assignment 1",
                    "Assignment 2",
                    "Assignment 3",
                    "Assignment 4",
                    "Assignment 5",
                    "Assignment 6",
                    "Assignment 7",
                    "Assignment 8",
                    "Assignment 9",
                    "Assignment 10",
                    "Assignment 11",
                    "Assignment 12",
                    "Assignment 13",
                    "Assignment 14",
                    "Assignment 15",
                    "Assignment 16",
                    "Assignment 17",
                    "Assignment 18",
                    "Assignment 19",
                    "Assignment 20",
                ],
            ),
            "description": self.fake.paragraph(),
            "deadline": self.fake.future_datetime(),
            "total_marks": self.fake.random_int(min=50, max=100),
        }

    @staticmethod
    def insert_mock_course(
        mock_lecturer: LecturerMockInsertionResult,
    ) -> CourseMockInsertionResult:
        # Insert mock course to database
        course_mocker = CourseMocker()
        course = course_mocker.mock_course()
        course["lecturer_id"] = mock_lecturer["lecturer_id"]

        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute(
            "INSERT INTO Course (course_code, course_name, semester, lecturer_id) VALUES (%s, %s, %s, %s)",
            (
                course["course_code"],
                course["course_name"],
                course["semester"],
                course["lecturer_id"],
            ),
        )
        db.commit()
        course_code = course["course_code"]
        return {
            "course_details": course,
            "course_code": course_code,
        }

    @staticmethod
    def enrol_mock_student(
        mock_course: CourseMockInsertionResult, mock_student: StudentMockInsertionResult
    ):
        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute(
            "INSERT INTO Enrollment (course_code, student_id) VALUES (%s, %s)",
            (mock_course["course_code"], mock_student["student_id"]),
        )
        db.commit()

    @staticmethod
    def insert_mock_assignment(
        mock_course: CourseMockInsertionResult,
    ) -> MockAssignment:
        # Insert mock assignment to database
        assignment_mocker = CourseMocker()
        assignment = assignment_mocker.mock_assignment()
        assignment["course_code"] = mock_course["course_code"]

        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute(
            "INSERT INTO Assignment (course_code, title, description, deadline, total_marks) VALUES (%s, %s, %s, %s, %s)",
            (
                assignment["course_code"],
                assignment["title"],
                assignment["description"],
                assignment["deadline"],
                assignment["total_marks"],
            ),
        )
        db.commit()
        assignment["assignment_id"] = db_cursor.lastrowid

        return assignment
