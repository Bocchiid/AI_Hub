from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.core.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timezone
from jose import JWTError, jwt
from src.database import user_repo
from src.user import schemas as user_schemas


# get token from url = '/login'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    验证并返回当前用户信息。
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        exp = payload.get("exp")

        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise credentials_exception
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    queried_user = await user_repo.query_user_by_id(user_id)

    if queried_user is None:
        raise credentials_exception

    return queried_user


async def get_current_user_id(user: dict = Depends(get_current_user)):
    """
    验证并返回当前用户 ID。
    """
    return user.get('_id')


class RoleChecker:
    def __init__(self, allowed_roles: list[user_schemas.UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: dict = Depends(get_current_user)):
        user_role = user.get("role", user_schemas.UserRole.USER)
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user


# 快捷依赖
admin_required = RoleChecker([user_schemas.UserRole.ADMIN])
user_required = RoleChecker([user_schemas.UserRole.USER, user_schemas.UserRole.ADMIN])