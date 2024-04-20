from typing import TypedDict
from faker import Faker


class MockFile(TypedDict):
    file_name: str
    file_content: str


class FileMocker:
    def __init__(self):
        self.fake = Faker()

    def mock_file(self) -> MockFile:
        return {
            "file_name": self.fake.file_name(),
            "file_content": self.fake.paragraphs(),
        }
