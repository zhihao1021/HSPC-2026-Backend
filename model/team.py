from pydantic import BaseModel, field_validator

from typing import Optional


class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class TeamRead(BaseModel):
    uid: str
    name: str

    @field_validator("uid", mode="before")
    @classmethod
    def convert_snowflake_to_str(cls, value: Optional[int]) -> Optional[str]:
        return str(value) if value is not None else None
