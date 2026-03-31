from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode, encode
from pydantic_snowflake import SnowflakeId

from os import getenv
from typing import Annotated, Union

from type import ScopeType

from .exceptions import INVALID_TOKEN, PERMISSION_DENIED
from .key import KEY_STORE
from .type import JWTPayload, JWTResponse

SECURITY = HTTPBearer(
    scheme_name="JWT",
    description="JWT which get from posting discord oauth code to /oauth"
)
KEY_ALGORITHM = getenv("JWT_KEY_ALG", "ES256")


def sign_token(payload: JWTPayload) -> JWTResponse:
    if not isinstance(payload, JWTPayload):
        payload = JWTPayload.model_validate(payload)

    data = payload.model_dump()
    token = encode(
        data,
        key=KEY_STORE.get_private_jwk(),
        algorithm=KEY_ALGORITHM
    )

    return JWTResponse(access_token=token)


def verify_token(token: Union[HTTPAuthorizationCredentials, str] = Depends(SECURITY)) -> JWTPayload:
    jwt = token if isinstance(token, str) else token.credentials
    try:
        payload_data = decode(
            jwt,
            key=KEY_STORE.get_public_jwk(),
            algorithms=[KEY_ALGORITHM],
            options={
                "require": ["exp", "iat"]
            },
        )
    except:
        raise INVALID_TOKEN

    return JWTPayload.model_validate(payload_data)


def get_user_id(jwt_payload: 'JWTPayloadDepends') -> SnowflakeId:
    if ScopeType.USE_IDENTITY not in jwt_payload.scopes:
        raise INVALID_TOKEN

    return SnowflakeId(jwt_payload.uid)


async def check_admin(jwt_payload: 'JWTPayloadDepends') -> None:
    if ScopeType.PERMISSION_ADMIN not in jwt_payload.scopes:
        raise PERMISSION_DENIED

jwt_payload_depends = Depends(verify_token)
JWTPayloadDepends = Annotated[JWTPayload, jwt_payload_depends]

user_id_depends = Depends(get_user_id)
UserIdDepends = Annotated[SnowflakeId, user_id_depends]

is_admin_depends = Depends(check_admin)
IsAdminDepends = Annotated[None, is_admin_depends]
