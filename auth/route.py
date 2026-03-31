from fastapi import APIRouter, Query, Response
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from enum import Enum

from .key import KEY_STORE
from .type import JWTPayload, JWTResponse
from .utils import JWTPayloadDepends, sign_token

from .basic.route import router as basic_auth_router
from .utils import KEY_ALGORITHM


class PublicKeyFormat(Enum):
    JWK = "JWK"
    PEM = "PEM"
    DER = "DER"


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
router.include_router(basic_auth_router)


@router.get("/algorithm")
def get_algorithm() -> str:
    return KEY_ALGORITHM


@router.get("/public-key")
def get_public_key(
    key_format: PublicKeyFormat = Query(PublicKeyFormat.JWK, alias="format")
):
    if key_format is None or key_format == PublicKeyFormat.JWK:
        return KEY_STORE.get_public_jwk(as_dict=True)
    elif key_format == PublicKeyFormat.PEM:
        return KEY_STORE.get_public_key().public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
    elif key_format == PublicKeyFormat.DER:
        bytes_content = KEY_STORE.get_public_key().public_bytes(
            encoding=Encoding.DER,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        return Response(
            content=bytes_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=\"public_key.der\""
            }
        )


@router.post("/refresh")
def refresh_token(
    jwt_payload: JWTPayloadDepends
) -> JWTResponse:
    return sign_token(JWTPayload(**jwt_payload.model_dump(exclude={"exp", "iat"})))
