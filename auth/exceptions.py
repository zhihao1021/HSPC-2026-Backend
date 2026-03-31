from fastapi import HTTPException, status

INVALID_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token"
)

PERMISSION_DENIED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Permission denied"
)
