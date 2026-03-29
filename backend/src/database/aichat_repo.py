# src/database/aichat_repo.py

from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List


async def query_chat_history(collection: AsyncIOMotorCollection,
                             user_id: str,
                             conversation_id: str):
    query_doc = {
        '_id': conversation_id,
        'user_id': user_id
    }

    projection_doc = {
        'user_id': False,
        '_id': False
    }

    cursor = collection.find(query_doc, projection_doc)
    ls = await cursor.to_list()

    if ls:
        return ls

    return []


async def upsert_chat_history(collection: AsyncIOMotorCollection,
                              user_id: str,
                              conversation_id: str,
                              title: str,
                              messages: List):
    query_doc = {
        '_id': conversation_id,
    }

    update_doc = {
        '$set': {
            'user_id': user_id,
            'title': title,
            'messages': messages
        }
    }

    await collection.update_one(
        query_doc,
        update_doc,
        upsert = True
    )


async def query_chat_history_list(collection: AsyncIOMotorCollection,
                                  user_id: str):
    query_doc = {
        'user_id': user_id
    }

    projection_doc = {
        'user_id': False,
        'messages': False
    }

    cursor = collection.find(query_doc, projection_doc)
    ls = await cursor.to_list()

    return ls