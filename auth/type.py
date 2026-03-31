from pydantic import BaseModel, Field, field_validator, field_serializer

from datetime import datetime, timedelta

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

from type import ScopeType


class JWTResponse(BaseModel):
    token_type: str = "bearer"
    access_token: str


class JWTPayload(BaseModel):
    uid: str
    exp: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(days=7)
    )
    iat: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    scopes: set[ScopeType] = Field(default_factory=set)

    @field_validator("uid", mode="before")
    @classmethod
    def convert_uid_to_str(cls, value: str) -> str:
        return str(value)

    @field_validator("exp", "iat", mode="after")
    def validate_datetime(cls, v: datetime) -> datetime:
        return v.astimezone(UTC)

    @field_serializer("scopes")
    def serialize_scopes(self, v: set[ScopeType]) -> list[str]:
        return [scope.value for scope in v]
