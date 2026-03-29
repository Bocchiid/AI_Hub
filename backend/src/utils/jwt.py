# src/utils/jwt.py

from datetime import datetime, timedelta, timezone
from jose import jwt
from src.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    """
    生成 JWT token
    data: 要写进 token 的信息, 例如 {'sub': user_id}
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # 添加过期时间

    # 使用 jose.jwt 编码
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt