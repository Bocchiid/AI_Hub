# src/ai_experience/model.py

from . import schemas as exp_schemas
from src.database.mongodb import db
from src.utils.tool import obj
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional, Dict, Any
from bson import ObjectId

ExperienceCollection: AsyncIOMotorCollection = db["AIExperience"]

async def add_experience(data: Dict[str, Any]):
    """
    添加 AI 体验案例
    """
    if "_id" not in data:
        data["_id"] = obj()
    
    # 自动计算 order: 获取当前最大 order 并 +1
    all_items = await get_experiences()
    if all_items:
        max_order = max(item.get("order", 0) for item in all_items)
        data["order"] = max_order + 1
    else:
        data["order"] = 1

    result = await ExperienceCollection.insert_one(data)
    return str(result.inserted_id)

async def get_experiences(query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    获取体验案例列表
    """
    cursor = ExperienceCollection.find(query).sort("order", 1)
    return await cursor.to_list(length=100)

async def get_experience_by_id(mongo_id: str) -> Optional[Dict[str, Any]]:
    """
    根据 ID 获取单个案例
    """
    return await ExperienceCollection.find_one({"_id": mongo_id})

async def update_experience(mongo_id: str, update_data: Dict[str, Any]):
    """
    更新体验案例
    """
    await ExperienceCollection.update_one(
        {"_id": mongo_id},
        {"$set": update_data}
    )
    return "Update successful"

async def delete_experience(mongo_id: str):
    """
    删除案例
    """
    await ExperienceCollection.delete_one({"_id": mongo_id})
    return "Delete successful"

async def delete_many_experiences(mongo_ids: List[str]):
    """
    批量删除案例
    """
    result = await ExperienceCollection.delete_many({"_id": {"$in": mongo_ids}})
    return f"Deleted {result.deleted_count} items"
