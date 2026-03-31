# src/user/schemas.py

from pydantic import BaseModel
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "administrator"


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    role: Optional[UserRole] = UserRole.USER


class UserRegisterResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True