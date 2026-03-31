from asyncpg import Connection

from typing import Optional, overload, Self, Union

from type import UidType

from .base import T, UidTableModel


class Team(UidTableModel):
    __table__ = "teams"

    name: str

    @overload
    @classmethod
    async def get_by_member_uid(
        cls,
        conn: Connection,
        member_uid: UidType,
        *,
        model_cls: None = None
    ) -> Optional[Self]: ...

    @overload
    @classmethod
    async def get_by_member_uid(
        cls,
        conn: Connection,
        member_uid: UidType,
        *,
        model_cls: type[T]
    ) -> Optional[T]: ...

    @classmethod
    async def get_by_member_uid(
        cls,
        conn: Connection,
        member_uid: UidType,
        *,
        model_cls: Optional[type[T]] = None
    ) -> Optional[Union[Self, T]]:
        fields = cls._check_field(model_cls, prefix="t.")

        row = await conn.fetchrow(f"""
            SELECT {', '.join(fields)} FROM {cls.__table__} t
            JOIN users u ON u.team_id = t.uid
            WHERE u.uid = $1
        """, int(member_uid))

        return (model_cls or cls)(**row) if row else None

    @classmethod
    async def exists_by_name(
        cls,
        conn: Connection,
        name: str
    ) -> bool:
        row = await conn.fetchrow(f"""
            SELECT 1 FROM {cls.__table__} WHERE name = $1
        """, name)


        return row is not None