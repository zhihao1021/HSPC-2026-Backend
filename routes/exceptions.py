from fastapi import HTTPException, status

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)

TEAM_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Team not found"
)

ALREADY_IN_TEAM = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User is already in a team"
)

TEAM_NAME_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Team name already exists"
)

TEAM_IS_FULL = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Team is full"
)

WRONG_PASSWORD = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Wrong password"
)

UPLOAD_IMAGE_FAILED = HTTPException(
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    detail="Failed to upload SID image"
)
