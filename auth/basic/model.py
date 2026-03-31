from pydantic import BaseModel, EmailStr


class LoginOrRegisterData(BaseModel):
    email: EmailStr
    password: str
