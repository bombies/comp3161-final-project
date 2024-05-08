from datetime import datetime
from typing import TypedDict
from faker import Faker

from modules.utils.db import db
from tests.mockers.course_mocker import CourseMockInsertionResult


class MockCalendarEvent(TypedDict):
    event_no: int
    course_id: str
    date: datetime
    event_name: str


class CalendarMocker:
    def __init__(self):
        self.fake = Faker()

    def mock_event(self):
        return MockCalendarEvent(
            event_no=1,
            course_id=self.fake.text(),
            date=self.fake.date_time_this_year(),
            event_name=self.fake.text(),
        )

    @staticmethod
    def insert_event(course: CourseMockInsertionResult):
        mock_event = CalendarMocker().mock_event()
        db_cursor = db.cursor()
        db_cursor.execute(
            "INSERT INTO CalendarEvent (course_id, date, event_name) VALUES (%s, %s, %s)",
            (course["course_code"], mock_event["date"], mock_event["event_name"]),
        )
        db.commit()
        event_no = db_cursor.lastrowid
        mock_event["event_no"] = event_no
        mock_event["course_id"] = course["course_code"]
        return mock_event
