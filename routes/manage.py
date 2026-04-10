from fastapi import APIRouter

from typing import Literal

from auth import is_admin_depends
from database import ConnDepends
from schemas.user import User
from type import VerifyState
from verify.email import VERIFY_MANAGER

from .exceptions import USER_NOT_FOUND, USER_DOES_NOT_HAVE_SID_IMAGE

router = APIRouter(
    prefix="/manage",
    tags=["Management"],
    dependencies=[is_admin_depends]
)


@router.put("/sid_verify/{uid}/{result}")
async def sid_verify(
    conn: ConnDepends,
    uid: int,
    result: Literal["pass", "fail"],
    force: bool = False,
) -> None:
    user = await User.get_by_uid(
        conn=conn,
        uid=uid,
    )
    if user is None:
        raise USER_NOT_FOUND
    if not force and user.verify_state == VerifyState.UNVERIFIED:
        raise USER_DOES_NOT_HAVE_SID_IMAGE

    await User.update_by_uid(
        conn=conn,
        uid=uid,
        data={
            "verify_state": VerifyState.VERIFIED if result == "pass" else VerifyState.FAILED
        }
    )

    await VERIFY_MANAGER.send_sid_email(result == "pass", user.email)
