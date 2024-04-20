import datetime
from typing import TypedDict
from faker import Faker

from modules.utils.db import db
from modules.utils.route_utils import create_missing_dirs, open_file
from tests.mockers.account_mocker import (
    LecturerMockInsertionResult,
    StudentMockInsertionResult,
)
from tests.mockers.file_mocker import FileMocker, MockFile


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
    deadline: datetime.datetime
    total_marks: float


class MockAssignmentSubmission(TypedDict):
    submission_id: int
    assignment_id: int
    student_id: int
    submission_time: datetime.datetime
    grade: float | None
    submission_time: datetime.datetime
    file_path: str


class MockCourseSection(TypedDict):
    section_id: int
    course_code: str
    section_name: str


class MockCourseSectionItem(TypedDict):
    item_id: int
    section_id: int
    title: str
    description: str | None
    deadline: datetime.datetime | None
    link: str | None
    file_location: str | None


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

    def mock_course_section(self) -> MockCourseSection:
        return {
            "section_id": self.fake.random_int(),
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
            "section_name": self.fake.random_element(
                [
                    "Lecture Notes",
                    "Tutorials",
                    "Assignments",
                    "Quizzes",
                    "Projects",
                    "Exams",
                    "Resources",
                    "Announcements",
                    "Discussion Forum",
                    "Feedback",
                ],
            ),
        }

    def mock_course_section_item(
        self, section: MockCourseSection | None = None
    ) -> tuple[MockCourseSectionItem, MockFile]:
        if not section:
            section = self.mock_course_section()

        mock_file = FileMocker().mock_file()
        mock_file_path = f"data/course-sections/{section['course_code']}/{section['section_id']}/{mock_file['file_name']}"
        create_missing_dirs(mock_file_path)
        with open_file(mock_file_path, "w") as file:
            file.write("\n".join(mock_file["file_content"]))

        return (
            {
                "item_id": self.fake.random_int(),
                "section_id": self.fake.random_int(),
                "title": self.fake.random_element(
                    [
                        "Lecture 1",
                        "Lecture 2",
                        "Lecture 3",
                        "Lecture 4",
                        "Lecture 5",
                        "Lecture 6",
                        "Lecture 7",
                        "Lecture 8",
                        "Lecture 9",
                        "Lecture 10",
                        "Tutorial 1",
                        "Tutorial 2",
                        "Tutorial 3",
                        "Tutorial 4",
                        "Tutorial 5",
                        "Tutorial 6",
                        "Tutorial 7",
                        "Tutorial 8",
                        "Tutorial 9",
                        "Tutorial 10",
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
                        "Quiz 1",
                        "Quiz 2",
                        "Quiz 3",
                        "Quiz 4",
                        "Quiz 5",
                        "Quiz 6",
                        "Quiz 7",
                        "Quiz 8",
                        "Quiz 9",
                        "Quiz 10",
                    ],
                ),
                "description": self.fake.paragraph(),
                "deadline": self.fake.future_datetime(),
                "link": self.fake.url(),
                "file_location": mock_file_path,
            },
            mock_file,
        )

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

    @staticmethod
    def insert_mock_submission(
        mock_assignment: MockAssignment,
        mock_student: StudentMockInsertionResult,
    ) -> MockAssignmentSubmission:
        db_cursor = db.cursor(dictionary=True)
        mock_file = FileMocker().mock_file()
        mock_file_path = f"data/assignments/{mock_assignment['assignment_id']}/{mock_student['student_id']}_{mock_file['file_name']}"

        # Save file to disk
        with open_file(mock_file_path, "w") as file:
            file.write("\n".join(mock_file["file_content"]))

        submission_time = datetime.datetime.now()

        db_cursor.execute(
            "INSERT INTO AssignmentSubmission (assignment_id, student_id, submission_time, file_path) VALUES (%s, %s, %s, %s)",
            (
                mock_assignment["assignment_id"],
                mock_student["student_id"],
                submission_time,
                mock_file_path,
            ),
        )
        db.commit()

        submission_id = db_cursor.lastrowid
        return {
            "submission_id": submission_id,
            "assignment_id": mock_assignment["assignment_id"],
            "student_id": mock_student["student_id"],
            "submission_time": submission_time,
            "grade": None,
            "file_path": mock_file_path,
        }

    @staticmethod
    def insert_mock_course_section(
        mock_course: CourseMockInsertionResult,
    ) -> MockCourseSection:
        db_cursor = db.cursor(dictionary=True)
        section_name = Faker().random_element(
            [
                "Lecture Notes",
                "Tutorials",
                "Assignments",
                "Quizzes",
                "Projects",
                "Exams",
                "Resources",
                "Announcements",
                "Discussion Forum",
                "Feedback",
            ]
        )

        db_cursor.execute(
            "INSERT INTO Sections (course_code, section_name) VALUES (%s, %s)",
            (mock_course["course_code"], section_name),
        )
        db.commit()
        section_id = db_cursor.lastrowid

        return {
            "section_id": section_id,
            "course_code": mock_course["course_code"],
            "section_name": section_name,
        }

    @staticmethod
    def insert_mock_course_section_item(
        mock_course_section: tuple[MockCourseSection, MockFile],
    ) -> MockCourseSectionItem:
        db_cursor = db.cursor(dictionary=True)
        mocker = CourseMocker()
        mock_item, mock_file = mocker.mock_course_section_item(mock_course_section)

        db_cursor.execute(
            "INSERT INTO SectionItems (section_id, title, file_location, description, deadline, link) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                mock_course_section["section_id"],
                mock_item["title"],
                mock_item["file_location"],
                mock_item["description"],
                mock_item["deadline"].strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                mock_item["link"],
            ),
        )
        db.commit()
        item_id = db_cursor.lastrowid

        return (
            {
                "item_id": item_id,
                "section_id": mock_course_section["section_id"],
                "title": mock_item["title"],
                "description": mock_item["description"],
                "deadline": mock_item["deadline"],
                "link": mock_item["link"],
                "file_location": mock_item["file_location"],
            },
            mock_file,
        )
