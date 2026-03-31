# src/user/model.py
from http import HTTPStatus

from fastapi import HTTPException, status
from . import schemas as user_schemas
from src.database import user_repo
from src.hashing import hash
from src.utils import jwt


async def register_user(user_register_request: user_schemas.UserRegisterRequest):
    queried_user = await user_repo.query_user_by_name(user_register_request.username)

    if queried_user:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "User already exists"
        )

    hashed_password = hash.hash_password(user_register_request.password)
    await user_repo.insert_user(
        user_register_request.username, 
        hashed_password, 
        user_register_request.role.value
    )
    return "User registered successfully"


async def login_user(user_login_request: user_schemas.UserLoginRequest):
    queried_user = await user_repo.query_user_by_name(user_login_request.username)

    if not queried_user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password"
        )

    if not hash.verify_password(user_login_request.password, queried_user.get('password')):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password"
        )

    access_token = jwt.create_access_token(
        data={'sub': queried_user.get('_id')},
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }