from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.core.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timezone
from jose import JWTError, jwt
from src.database import user_repo


# get token from url = '/login'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """
    从 Authorization 头部提取 Bearer token，
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

    return user_id