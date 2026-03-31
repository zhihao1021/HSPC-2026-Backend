from pydantic import BaseModel, EmailStr, field_validator

from typing import Optional

from type import CityType, LunchType, VerifyState


class UserUpdate(BaseModel):
    origin_password: Optional[str] = None
    password: Optional[str] = None
    city: Optional[CityType] = None
    lunch: Optional[LunchType] = None
    real_name: Optional[str] = None
    school: Optional[str] = None
    is_nanbao: Optional[bool] = None
    is_graduate: Optional[bool] = None


class UserRead(BaseModel):
    uid: str
    email: EmailStr
    city: Optional[CityType] = None
    lunch: Optional[LunchType] = None
    real_name: Optional[str] = None
    school: Optional[str] = None
    team_id: Optional[str] = None
    is_nanbao: bool = False
    is_graduate: bool = False
    email_verified: bool = False
    student_verified: bool = False
    verify_state: VerifyState = VerifyState.UNVERIFIED

    @field_validator("uid", "team_id", mode="before")
    @classmethod
    def convert_snowflake_to_str(cls, value: Optional[int]) -> Optional[str]:
        return str(value) if value is not None else None
