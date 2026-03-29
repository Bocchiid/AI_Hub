# src/hashing/hash.py

from passlib.context import CryptContext

# 创建加密上下文，指定算法为 bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# encrypt password
def hash_password(password):
    return pwd_context.hash(password)

# verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)