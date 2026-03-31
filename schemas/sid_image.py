from pydantic_snowflake import SnowflakeId

from datetime import datetime

from .base import UidTableModel


class SidImage(UidTableModel):
    __table__ = "sid_image"

    user_uid: SnowflakeId
    image_front: bytes
    image_back: bytes
    last_updated: datetime
