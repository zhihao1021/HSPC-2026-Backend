from asyncpg import Connection
from pydantic_snowflake import SnowflakeId

from typing import Optional, overload, Self, Union

from type import SidImageType, UidType

from .base import T, UidTableModel


class SidImage(UidTableModel):
    __table__ = "sid_image"

    user_uid: SnowflakeId
    image_front: bytes
    image_back: bytes

    @overload
    @classmethod
    async def get_by_user_uid(
        cls,
        conn: Connection,
        user_uid: UidType,
        *,
        model_cls: None = None
    ) -> Optional[Self]: ...

    @overload
    @classmethod
    async def get_by_user_uid(
        cls,
        conn: Connection,
        user_uid: UidType,
        *,
        model_cls: type[T]
    ) -> Optional[T]: ...

    @classmethod
    async def get_by_user_uid(
        cls,
        conn: Connection,
        user_uid: UidType,
        *,
        model_cls: Optional[type[T]] = None
    ) -> Optional[Union[Self, T]]:
        fields = cls._check_field(model_cls)

        row = await conn.fetchrow(f"""
            SELECT {', '.join(fields)} FROM {cls.__table__}
            WHERE user_uid = $1
        """, int(user_uid))

        return (model_cls or cls)(**row) if row else None

    @classmethod
    async def upsert_image_by_user_uid(
        cls,
        conn: Connection,
        user_uid: UidType,
        image_type: SidImageType,
        data: bytes
    ) -> None:
        new_uid = cls._generate_uid()
        await conn.execute(f"""
            INSERT INTO {cls.__table__} (uid, user_uid, image_{image_type})
            VALUES ($1, $2, $3)
            ON CONFLICT (user_uid) DO UPDATE
            SET image_{image_type} = EXCLUDED.image_{image_type}
        """, int(new_uid), int(user_uid), data)
