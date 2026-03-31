from asyncpg import Connection
from pydantic import EmailStr
from pydantic_snowflake import SnowflakeId, SnowflakeGenerator

from typing import Optional, overload, Self, Union

from type import CityType, LunchType, UidType

from .base import T, UidTableModel

user_id_generator = SnowflakeGenerator()


class User(UidTableModel):
    __table__ = "users"

    email: EmailStr
    password_hash: str
    city: Optional[CityType] = None
    lunch: Optional[LunchType] = None
    real_name: Optional[str] = None
    school: Optional[str] = None
    is_nanbao: bool = False
    is_graduate: bool = False
    team_id: Optional[SnowflakeId] = None
    email_verified: bool = False
    student_verified: bool = False
    verify_info: str = ""
    is_admin: bool = False

    @classmethod
    async def get_uid_password_hash_is_admin_by_email(
        cls,
        conn: Connection,
        email: str
    ) -> Optional[tuple[SnowflakeId, str, bool]]:
        row = await conn.fetchrow(f"""
            SELECT uid, password_hash, is_admin FROM {cls.__table__} 
            WHERE email = $1
        """, email)

        return (
            SnowflakeId(row["uid"]),
            row["password_hash"],
            row["is_admin"],
        ) if row else None

    @classmethod
    async def get_password_hash_by_uid(
        cls,
        conn: Connection,
        uid: UidType
    ) -> Optional[str]:
        row = await conn.fetchrow(f"""
            SELECT password_hash FROM {cls.__table__} 
            WHERE uid = $1
        """, int(uid))

        return row["password_hash"] if row else None

    @classmethod
    async def get_team_id_by_uid(
        cls,
        conn: Connection,
        uid: UidType
    ) -> Optional[SnowflakeId]:
        row = await conn.fetchrow(f"""
            SELECT team_id FROM {cls.__table__} 
            WHERE uid = $1
        """, int(uid))

        return SnowflakeId(row["team_id"]) if row and row["team_id"] is not None else None

    @overload
    @classmethod
    async def get_users_by_team_id(
        cls,
        conn: Connection,
        team_id: UidType,
        *,
        model_cls: None = None
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def get_users_by_team_id(
        cls,
        conn: Connection,
        team_id: UidType,
        *,
        model_cls: type[T]
    ) -> list[T]: ...

    @classmethod
    async def get_users_by_team_id(
        cls,
        conn: Connection,
        team_id: UidType,
        *,
        model_cls: Optional[type[T]] = None
    ) -> Union[list[Self], list[T]]:
        fields = cls._check_field(model_cls)

        row = await conn.fetch(f"""
            SELECT {', '.join(fields)} FROM {cls.__table__}
            WHERE team_id = $1
        """, int(team_id))

        if model_cls:
            return [model_cls(**r) for r in row]
        return [cls(**r) for r in row]

    @classmethod
    async def exists_by_email(cls, conn: Connection, email: str) -> bool:
        row = await conn.fetchrow(f"""
            SELECT 1 FROM {cls.__table__} WHERE email = $1
        """, email)
        return row is not None

    @classmethod
    async def check_is_admin_by_uid(cls, conn: Connection, uid: UidType) -> bool:
        row = await conn.fetchrow(f"""
            SELECT is_admin FROM {cls.__table__} WHERE uid = $1
        """, int(uid))

        return row["is_admin"] if row else False

    @classmethod
    async def check_have_team_by_uid(cls, conn: Connection, uid: UidType) -> bool:
        row = await conn.fetchrow(f"""
            SELECT team_id FROM {cls.__table__} WHERE uid = $1
        """, int(uid))

        return row["team_id"] is not None if row else False

    @classmethod
    async def update_team_id_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        team_id: Optional[UidType]
    ) -> None:
        await conn.execute(f"""
            UPDATE {cls.__table__} SET team_id = $1 WHERE uid = $2
        """, int(team_id) if team_id is not None else None, int(uid))
