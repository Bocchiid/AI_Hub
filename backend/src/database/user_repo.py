# src/database/user_repo.py

from .mongodb import db
from src.utils.tool import obj


UserCollection = db['Users']

async def query_user_by_name(username: str):
    query_doc = {
        'username': username
    }

    res = await UserCollection.find_one(query_doc)
    return res


async def insert_user(username: str, hashed_password: str, role: str):
    new_doc = {
        '_id': obj(),
        'username': username,
        'password': hashed_password,
        'role': role
    }

    await UserCollection.insert_one(new_doc)


async def query_user_by_id(user_id: str):
    query_doc = {
        '_id': user_id
    }

    res = await UserCollection.find_one(query_doc)
    return res