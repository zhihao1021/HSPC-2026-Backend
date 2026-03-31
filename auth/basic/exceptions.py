from fastapi import HTTPException, status

AUTHORIZE_FAILED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authorization failed."
)

REGISTER_FAILED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Registration failed."
)

CF_VALIDATION_FAILED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cloudflare Turnstile validation failed."
)
