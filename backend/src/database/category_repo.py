# src/database/category_repo.py

from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


async def insert_category(collection: AsyncIOMotorCollection, category_data: dict):
    """
    插入新分类
    """
    await collection.insert_one(category_data)


async def delete_category(collection: AsyncIOMotorCollection, _id: str):
    """
    根据 _id 删除分类
    """
    result = await collection.delete_one({"_id": ObjectId(_id)})
    return result.deleted_count > 0


async def update_category(collection: AsyncIOMotorCollection, _id: str, update_data: dict):
    """
    更新分类信息
    """
    await collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set": update_data}
    )


async def update_item_order(collection: AsyncIOMotorCollection, _id: str, new_order: int):
    """
    更新单个文档的 order
    """
    await collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set": {"order": new_order}}
    )


async def move_ai_links_to_category(collection: AsyncIOMotorCollection, old_category_id: str, new_category_id: str):
    """
    批量将某个分类下的所有 AI 链接转移到新分类
    """
    await collection.update_many(
        {"category_id": old_category_id},
        {"$set": {"category_id": new_category_id}}
    )


async def query_categories(collection: AsyncIOMotorCollection, filter_query: dict = None):
    """
    通用查询分类列表，支持过滤和排序
    """
    if filter_query is None:
        filter_query = {}
    
    cursor = collection.find(filter_query).sort('order', 1)
    ls = []
    async for doc in cursor:
        doc['_id'] = str(doc['_id'])
        ls.append(doc)
    return ls


async def query_category(collection: AsyncIOMotorCollection, filter_query: dict):
    """
    通用查询单个分类
    """
    doc = await collection.find_one(filter_query)
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


async def query_max_order(collection: AsyncIOMotorCollection, filter_query: dict = None):
    """
    查询当前集合中最大的 order
    """
    if filter_query is None:
        filter_query = {}
        
    cursor = collection.find(filter_query).sort('order', -1).limit(1)
    ls = await cursor.to_list(length=1)

    if ls:
        return ls[0].get('order', 0)

    return 0

