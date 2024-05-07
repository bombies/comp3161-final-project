from datetime import datetime
from typing import TypedDict
from faker import Faker
from tests.mockers.account_mocker import (
    LecturerMockInsertionResult,
    StudentMockInsertionResult,
)
from tests.mockers.course_mocker import CourseMockInsertionResult

from modules.utils.db import db


class MockForum(TypedDict):
    forum_id: int
    topic: str
    post_time: datetime
    creator: int
    course_code: str


class MockDiscussionThread(TypedDict):
    thread_id: int
    replies: int
    timeStamp: datetime
    forum_id: int


class MockDiscussionReply(TypedDict):
    reply_id: int
    thread_id: int
    user_id: int
    reply_time: datetime
    reply_text: str


class ForumMocker:
    def __init__(self):
        self.fake = Faker()

    def mock_forum(self, creator: int) -> MockForum:
        return {
            "forum_id": self.fake.random_int(),
            "topic": self.fake.text(),
            "post_time": self.fake.date_time(),
            "creator": creator,
            "course_code": self.fake.word(),
        }

    def mock_discussion_thread(self, forum_id: int) -> MockDiscussionThread:
        return {
            "thread_id": self.fake.random_int(),
            "replies": self.fake.random_int(),
            "timeStamp": self.fake.date_time(),
            "forum_id": forum_id,
        }

    def mock_discussion_reply(
        self, thread_id: int, user_id: int
    ) -> MockDiscussionReply:
        return {
            "reply_id": self.fake.random_int(),
            "thread_id": thread_id,
            "user_id": user_id,
            "reply_time": self.fake.date_time(),
            "reply_text": self.fake.text(),
        }

    @staticmethod
    def insert_mock_forum(
        mock_lecturer: LecturerMockInsertionResult,
        mock_course: CourseMockInsertionResult,
    ) -> MockForum:
        db_cursor = db.cursor(dictionary=True)
        mock_forum = ForumMocker().mock_forum(mock_lecturer["account_id"])
        db_cursor.execute(
            "INSERT INTO DiscussionForum (topic, post_time, creator, course_code) VALUES (%s, %s, %s, %s)",
            (
                mock_forum["topic"],
                mock_forum["post_time"],
                mock_lecturer["account_id"],
                mock_course["course_code"],
            ),
        )
        db.commit()
        mock_forum_id = db_cursor.lastrowid
        mock_forum["forum_id"] = mock_forum_id
        return mock_forum

    @staticmethod
    def insert_mock_discussion_thread(
        mock_forum: MockForum,
    ) -> MockDiscussionThread:
        db_cursor = db.cursor(dictionary=True)
        mock_thread = ForumMocker().mock_discussion_thread(mock_forum["forum_id"])
        db_cursor.execute(
            "INSERT INTO DiscussionThread (replies, timeStamp, forum_id) VALUES (%s, %s, %s)",
            (
                mock_thread["replies"],
                mock_thread["timeStamp"],
                mock_thread["forum_id"],
            ),
        )
        db.commit()
        mock_thread_id = db_cursor.lastrowid
        mock_thread["thread_id"] = mock_thread_id
        mock_thread["replies"] = 0
        return mock_thread

    @staticmethod
    def insert_mock_discussion_reply(
        mock_thread: MockDiscussionThread,
        mock_student: StudentMockInsertionResult,
    ) -> MockDiscussionReply:
        db_cursor = db.cursor(dictionary=True)
        mock_reply = ForumMocker().mock_discussion_reply(
            mock_thread["thread_id"], mock_student["account_id"]
        )
        db_cursor.execute(
            "INSERT INTO DiscussionReply (thread_id, user_id, reply_time, reply_text) VALUES (%s, %s, %s, %s)",
            (
                mock_reply["thread_id"],
                mock_student["account_id"],
                mock_reply["reply_time"],
                mock_reply["reply_text"],
            ),
        )
        db.commit()
        mock_reply_id = db_cursor.lastrowid
        mock_reply["reply_id"] = mock_reply_id
        return mock_reply
