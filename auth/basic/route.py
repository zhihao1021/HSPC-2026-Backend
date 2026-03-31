from fastapi import APIRouter, Body, Depends, Request

from typing import Annotated

from database import ConnDepends
from verify.cloudflare import CloudflareTurnstile
from verify.email import VERIFY_MANAGER
from type import ScopeType

from .auth import check_credentials, register_user
from .exceptions import CF_VALIDATION_FAILED
from .model import LoginOrRegisterData
from ..type import JWTPayload, JWTResponse
from ..utils import sign_token

router = APIRouter(
    prefix=""
)
cloudflare_turnstile = CloudflareTurnstile()


async def check_turnstile(
    token: Annotated[str, Body(embed=True)],
    request: Request
) -> None:
    remote_ip = request.client.host if request.client else None

    if not await cloudflare_turnstile.validate(
        token=token,
        remoteip=remote_ip
    ):
        raise CF_VALIDATION_FAILED

turnstile_depends = Depends(check_turnstile)


@router.post("/login", dependencies=[turnstile_depends])
async def auth(conn: ConnDepends, data: LoginOrRegisterData) -> JWTResponse:
    uid, is_admin = await check_credentials(
        conn=conn,
        data=data
    )

    scopes = set([ScopeType.USE_IDENTITY])
    if is_admin:
        scopes.add(ScopeType.PERMISSION_ADMIN)

    return sign_token(JWTPayload(
        uid=str(uid),
        scopes=scopes
    ))


@router.post("/register", dependencies=[turnstile_depends])
async def register(conn: ConnDepends, data: LoginOrRegisterData) -> JWTResponse:
    uid = await register_user(
        conn=conn,
        data=data
    )

    return sign_token(JWTPayload(uid=str(uid), scopes=set([ScopeType.USE_IDENTITY])))


@router.post("/verify-email")
async def verify_email(
    conn: ConnDepends,
    code: Annotated[str, Body(embed=True)]
) -> JWTResponse:
    uid = await VERIFY_MANAGER.verify_code(conn=conn, code=code)

    return sign_token(JWTPayload(uid=str(uid), scopes=set([ScopeType.USE_IDENTITY])))
