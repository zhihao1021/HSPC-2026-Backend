from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter
from pydantic_snowflake import SnowflakeId

from auth import is_admin_depends, UserIdDepends
from database import ConnDepends
from model.user import UserRead, UserUpdate
from schemas.user import User

from .exceptions import USER_NOT_FOUND, WRONG_PASSWORD


router = APIRouter(
    prefix="/user",
    tags=["User Management"],
)


@router.get("")
async def get_user_info(conn: ConnDepends, uid: UserIdDepends) -> UserRead:
    user_read = await User.get_by_uid(
        conn=conn,
        uid=uid,
        model_cls=UserRead
    )

    if user_read is None:
        raise USER_NOT_FOUND

    return user_read


@router.put("")
async def update_user_info(
    conn: ConnDepends,
    uid: UserIdDepends,
    data: UserUpdate
) -> UserRead:
    data_dump = data.model_dump(exclude_unset=True)
    if data.password and data.origin_password:
        password_hash = await User.get_password_hash_by_uid(
            conn=conn,
            uid=uid,
        )
        if password_hash is None:
            raise USER_NOT_FOUND

        if not checkpw(data.origin_password.encode(), password_hash.encode()):
            raise WRONG_PASSWORD

        data_dump["password_hash"] = hashpw(
            data.password.encode(),
            gensalt()
        ).decode()

    user_read = await User.update_by_uid(
        conn=conn,
        uid=uid,
        data=data.model_dump(exclude_unset=True),
        return_result=True,
        model_cls=UserRead
    )

    if user_read is None:
        raise USER_NOT_FOUND

    return user_read


@router.get("/all", dependencies=[is_admin_depends])
async def get_all_users(conn: ConnDepends) -> list[UserRead]:
    return await User.get_all(
        conn=conn,
        model_cls=UserRead
    )


@router.get("/by-id/{uid}", dependencies=[is_admin_depends])
async def get_user_info_by_uid(
    conn: ConnDepends,
    uid: SnowflakeId,
) -> UserRead:
    user_read = await User.get_by_uid(
        conn=conn,
        uid=uid,
        model_cls=UserRead
    )

    if user_read is None:
        raise USER_NOT_FOUND

    return user_read
