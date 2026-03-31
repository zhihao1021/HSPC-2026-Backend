from enum import Enum


class ScopeType(str, Enum):
    USE_IDENTITY = "use:identity"
    USE_EMAIL = "use:email"
    PERMISSION_ADMIN = "permission:admin"
