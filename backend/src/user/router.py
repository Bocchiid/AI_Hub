# src/user/router.py

from fastapi import APIRouter, Depends
from . import schemas as user_schemas
from . import model as user_model
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    tags = ["User"]
)

@router.post("/register", response_model = user_schemas.UserRegisterResponse)
async def register_user(user_register_request: user_schemas.UserRegisterRequest):
    response = await user_model.register_user(user_register_request)
    return user_schemas.UserRegisterResponse(
        message = response
    )


@router.post("/login", response_model = user_schemas.UserLoginResponse)
async def login_user(form: OAuth2PasswordRequestForm = Depends()):
    user_login_request = user_schemas.UserLoginRequest(
        username = form.username,
        password = form.password
    )

    response = await user_model.login_user(user_login_request)
    return user_schemas.UserLoginResponse(
        access_token = response.get('access_token'),
        token_type = response.get('token_type')
    )