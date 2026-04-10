from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Path, UploadFile
from pydantic_snowflake import SnowflakeId

from typing import Annotated, Optional

from auth import is_admin_depends, UserIdDepends
from database import ConnDepends
from model.sid_image import SidImageRead
from model.user import UserRead, UserUpdate
from schemas.sid_image import SidImage
from schemas.user import User
from type import SidImageType
from verify.image_converter import ImageConverter

from .exceptions import USER_NOT_FOUND, WRONG_PASSWORD, UPLOAD_IMAGE_FAILED


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


@router.get("/sid")
async def get_sid_image(
    conn: ConnDepends,
    uid: UserIdDepends,
) -> Optional[SidImageRead]:
    return await SidImage.get_by_user_uid(
        conn=conn,
        user_uid=uid,
        model_cls=SidImageRead
    )


@router.put("/sid/{sid_type}")
async def upload_sid_image(
    conn: ConnDepends,
    uid: UserIdDepends,
    sid_type: Annotated[SidImageType, Path()],
    image: UploadFile
) -> None:
    sid_image = await ImageConverter.convert_to_jpeg(await image.read())
    if sid_image is None:
        raise UPLOAD_IMAGE_FAILED

    await SidImage.upsert_image_by_user_uid(
        conn=conn,
        user_uid=uid,
        image_type=sid_type,
        data=sid_image
    )


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


@router.get("/by-id/{uid}/sid", dependencies=[is_admin_depends])
async def get_user_sid_image_by_uid(
    conn: ConnDepends,
    uid: SnowflakeId,
) -> Optional[SidImageRead]:
    return await SidImage.get_by_user_uid(
        conn=conn,
        user_uid=uid,
        model_cls=SidImageRead
    )
