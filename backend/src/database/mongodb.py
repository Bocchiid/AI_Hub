# src/database/mongodb.py

from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import MONGODB_URL, DATABASE_NAME


client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]


async def test_connection():
    try:
        await client.admin.command('ping')
        print('MongoDB Connection OK')
    except Exception as e:
        print('MongoDB Connection Error')