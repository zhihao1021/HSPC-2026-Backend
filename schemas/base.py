from asyncpg import Connection
from pydantic import BaseModel, Field, model_validator
from pydantic_snowflake import SnowflakeId, SnowflakeGenerator

from typing import (
    Any,
    ClassVar,
    Literal,
    Mapping,
    Optional,
    overload,
    Self,
    Type,
    TypeVar,
    Union
)

from type import UidType

_generator_map: dict[str, SnowflakeGenerator] = {}

T = TypeVar("T", bound=BaseModel)


class TableModel(BaseModel):
    __table__: ClassVar[str]


class UidTableModel(TableModel):
    uid: SnowflakeId = Field(default=SnowflakeId(
        0), description="The unique identifier of the record.")

    @classmethod
    def _check_field(cls, model_cls: Optional[Type[T]], prefix: str = "") -> set[str]:
        if model_cls is None:
            return set([f"{prefix}*"])

        self_fields = set([
            field.alias if field.alias else name
            for name, field in cls.model_fields.items()
        ])
        model_fields = set(model_cls.model_fields.keys())

        if not model_fields.issubset(self_fields):
            missing = ', '.join(model_fields - self_fields)
            raise ValueError(f"Fields {missing} not found in {cls.__name__}.")

        return set([f"{prefix}{field}" for field in model_fields])

    @model_validator(mode="before")
    @classmethod
    def generate_uid(cls, values: dict) -> dict:
        if "uid" not in values:
            generator = _generator_map.get(cls.__table__)
            if generator is None:
                generator = SnowflakeGenerator()
                _generator_map[cls.__table__] = generator
            values["uid"] = generator.next()
        return values

    async def save(self, conn: Connection) -> None:
        fields = self.__class__.model_fields.keys()

        field_names = [
            field.alias if field.alias else name
            for name, field in self.__class__.model_fields.items()
        ]
        values = [getattr(self, field) for field in fields]

        await conn.execute(f"""
            INSERT INTO {self.__table__} ({', '.join(field_names)}) 
            VALUES ({', '.join(['$' + str(i + 1) for i in range(len(values))])})
            ON CONFLICT (uid) DO UPDATE 
            SET {', '.join([f"{name} = EXCLUDED.{name}" for name in field_names])}
            """, *values
        )

    def to_model(self, model_cls: Type[T]) -> T:
        fields_map = {
            field.alias if field.alias else name: name
            for name, field in self.__class__.model_fields.items()
        }

        for model_field in model_cls.model_fields.keys():
            if model_field not in fields_map:
                raise ValueError(
                    f"Field {model_field} not found in {self.__class__.__name__}.")

        return model_cls(**{
            model_field: getattr(self, fields_map[model_field])
            for model_field in model_cls.model_fields.keys()
        })

    @overload
    @classmethod
    async def get_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        *,
        model_cls: None = None
    ) -> Optional[Self]: ...

    @overload
    @classmethod
    async def get_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        *,
        model_cls: Type[T]
    ) -> Optional[T]: ...

    @classmethod
    async def get_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        *,
        model_cls: Optional[Type[T]] = None
    ) -> Optional[Union[Self, T]]:
        fields = cls._check_field(model_cls)

        row = await conn.fetchrow(f"""
            SELECT {', '.join(fields)} FROM {cls.__table__} WHERE uid = $1
            """, int(uid)
        )

        return (model_cls or cls)(**row) if row else None

    @overload
    @classmethod
    async def get_all(
        cls,
        conn: Connection,
        *,
        model_cls: None = None,
        seek: Optional[SnowflakeId] = None,
        limit: Optional[int] = None
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def get_all(
        cls,
        conn: Connection,
        *,
        model_cls: Type[T],
        seek: Optional[SnowflakeId] = None,
        limit: Optional[int] = None
    ) -> list[T]: ...

    @classmethod
    async def get_all(
        cls,
        conn: Connection,
        *,
        model_cls: Optional[Type[T]] = None,
        seek: Optional[SnowflakeId] = None,
        limit: Optional[int] = None
    ) -> Union[list[Self], list[T]]:
        fields = cls._check_field(model_cls)

        row = await conn.fetch(f"""
            SELECT {', '.join(fields)} FROM {cls.__table__}
            WHERE ($1::bigint IS NULL OR uid > $1)
            ORDER BY uid DESC
            {f"LIMIT {limit}" if limit is not None else ""}
            """, int(seek) if seek else None
        )

        if model_cls:
            return [model_cls(**record) for record in row]
        return [cls(**record) for record in row]

    @classmethod
    async def exists_by_uid(cls, conn: Connection, uid: UidType) -> bool:
        row = await conn.fetchrow(f"""
            SELECT 1 FROM {cls.__table__} WHERE uid = $1
            """, int(uid)
        )

        return row is not None

    @overload
    @classmethod
    async def update_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        data: Mapping[str, Any],
        *,
        return_result: Literal[False] = False,
        model_cls: Optional[Type[T]] = None,
    ) -> None: ...

    @overload
    @classmethod
    async def update_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        data: Mapping[str, Any],
        *,
        return_result: Literal[True] = True,
        model_cls: None = None,
    ) -> Optional[Self]: ...

    @overload
    @classmethod
    async def update_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        data: Mapping[str, Any],
        *,
        return_result: Literal[True] = True,
        model_cls: Type[T],
    ) -> Optional[T]: ...

    @classmethod
    async def update_by_uid(
        cls,
        conn: Connection,
        uid: UidType,
        data: Mapping[str, Any],
        *,
        return_result: bool = False,
        model_cls: Optional[Type[T]] = None,
    ) -> Optional[Union[Self, T]]:
        self_fields = set(cls.model_fields.keys())
        update_fields = set([field for field in data.keys()])

        if not update_fields.issubset(self_fields):
            missing = ', '.join(update_fields - self_fields)
            raise ValueError(f"Fields {missing} not found in {cls.__name__}.")

        if not update_fields:
            return await cls.get_by_uid(conn, uid, model_cls=model_cls) if return_result else None

        update_field_list = list(update_fields)
        values = [data[field] for field in update_field_list]

        update_field_string = ', '.join([
            f"{field} = ${i}"
            for i, field in enumerate(update_field_list, 2)]
        )

        stat = f"""
        UPDATE {cls.__table__}
        SET {update_field_string}
        WHERE uid = $1
        {f"RETURNING {', '.join(cls._check_field(model_cls))}" if return_result else ""}
        """
        if not return_result:
            await conn.execute(stat, int(uid), *values)
            return

        row = await conn.fetchrow(stat, int(uid), *values)
        return (model_cls or cls)(**row) if row else None

    @classmethod
    async def delete_by_uid(cls, conn: Connection, uid: UidType) -> None:
        await conn.execute(f"""
            DELETE FROM {cls.__table__} WHERE uid = $1
            """, int(uid)
        )
