# src/user/schemas.py

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    username: str
    password: str


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