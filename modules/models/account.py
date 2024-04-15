from dataclasses import dataclass
from enum import Enum, EnumMeta
from typing import NewType


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


AccountType = BaseEnum("AccountType", ["Admin", "Lecturer", "Student"])


@dataclass
class Account:
    account_id: int
    email: str
    password: str
    account_type: AccountType
    contact_info: str
    name: str


TAccount = NewType("Account", Account)
