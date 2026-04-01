from pydantic import BaseModel, Field, field_validator

from typing import Optional


class TeamCreate(BaseModel):
    name: str = Field(min_length=1)


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)


class TeamRead(BaseModel):
    uid: str
    name: str = Field(min_length=1)

    @field_validator("uid", mode="before")
    @classmethod
    def convert_snowflake_to_str(cls, value: Optional[int]) -> Optional[str]:
        return str(value) if value is not None else None
