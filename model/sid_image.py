from pydantic import BaseModel, field_validator

from base64 import b64encode
from typing import Optional


class SidImageRead(BaseModel):
    uid: str
    user_uid: str
    image_front: str
    image_back: str

    @field_validator("uid", "user_uid", mode="before")
    @classmethod
    def convert_snowflake_to_str(cls, value: Optional[int]) -> Optional[str]:
        return str(value) if value is not None else None

    @field_validator("image_front", "image_back", mode="before")
    @classmethod
    def convert_bytes_to_base64(cls, value: Optional[bytes]) -> Optional[str]:
        return b64encode(value).decode("utf-8") if value is not None else None
