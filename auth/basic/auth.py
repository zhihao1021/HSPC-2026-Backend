from asyncpg import Connection
from bcrypt import checkpw, gensalt, hashpw
from pydantic_snowflake import SnowflakeId

from schemas.email_history import EmailHistory
from schemas.user import User
from verify.email import VERIFY_MANAGER

from .model import LoginOrRegisterData
from .exceptions import AUTHORIZE_FAILED, REGISTER_FAILED, RESEND_TOO_FREQUENT


async def check_credentials(conn: Connection, data: LoginOrRegisterData) -> tuple[SnowflakeId, bool]:
    result = await User.get_uid_password_hash_is_admin_by_email(
        conn=conn,
        email=data.email
    )
    if result is None:
        raise AUTHORIZE_FAILED

    uid, stored_hash, is_admin = result

    if not checkpw(data.password.encode(), stored_hash.encode()):
        raise AUTHORIZE_FAILED

    return uid, is_admin


async def register_user(conn: Connection, data: LoginOrRegisterData) -> SnowflakeId:
    if await User.exists_by_email(conn, data.email):
        raise REGISTER_FAILED

    user = User(
        email=data.email,
        password_hash=hashpw(data.password.encode(), gensalt()).decode()
    )
    await user.save(conn=conn)

    await EmailHistory.get_email_if_can_resend(conn, user.uid)
    await VERIFY_MANAGER.send_verify_email(
        uid=str(user.uid),
        email=data.email
    )

    return user.uid


async def resend_verification_email(conn: Connection, uid: SnowflakeId) -> None:
    if not await User.exists_by_uid(conn, uid):
        raise AUTHORIZE_FAILED

    email = await EmailHistory.get_email_if_can_resend(conn, uid)
    if email is None:
        raise RESEND_TOO_FREQUENT

    await VERIFY_MANAGER.send_verify_email(
        uid=str(uid),
        email=email
    )
