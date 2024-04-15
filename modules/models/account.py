from dataclasses import dataclass
from enum import Enum
from typing import NewType

AccountType = Enum("AccountType", ["Admin", "Lecturer", "Student"])


@dataclass
class Account:
    account_id: int
    email: str
    password: str
    account_type: AccountType
    contact_info: str
    name: str


TAccount = NewType("Account", Account)
