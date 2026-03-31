from enum import Enum


class VerifyState(int, Enum):
    UNVERIFIED = 0
    PENDING = 1
    VERIFIED = 2
    FAILED = 3
