# src/database/ai_link_repo.py

from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


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


async def update_item_order(collection: AsyncIOMotorCollection, _id: str, new_order: int):
    """
    更新单个文档的 order
    """
    await collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set": {"order": new_order}}
    )


async def query_ai_links(collection: AsyncIOMotorCollection, 
                           category_id: str = None):
    """
    查询 AIHub 集合中的 AI 外部链接
    category_id: 可选的分类筛选
    """

    query_doc = {}
    if category_id:
        query_doc['category_id'] = category_id

    # 按 order 升序排序
    cursor = collection.find(query_doc).sort('order', 1)
    ls = []
    async for doc in cursor:
        doc['_id'] = str(doc['_id'])
        ls.append(doc)

    return ls


async def insert_ai_link(collection: AsyncIOMotorCollection,
                         ai_data: dict):
    """
    向 AIHub 集合中插入新的 AI 链接数据
    """

    await collection.insert_one(ai_data)


async def delete_ai_link(collection: AsyncIOMotorCollection,
                         _id: str):
    """
    根据 MongoDB 的 _id 删除指定的 AI 链接
    """
    result = await collection.delete_one({"_id": ObjectId(_id)})
    return result.deleted_count > 0


async def delete_ai_links_batch(collection: AsyncIOMotorCollection, ids: list[str]):
    """
    批量删除 AI 链接
    """
    result = await collection.delete_many({"_id": {"$in": [ObjectId(i) for i in ids]}})
    return result.deleted_count


async def update_ai_link(collection: AsyncIOMotorCollection, _id: str, update_data: dict):
    """
    更新 AI 链接信息
    """
    await collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set": update_data}
    )


async def batch_move_ai_links(collection: AsyncIOMotorCollection, ids: list[str], new_category_id: str):
    """
    批量移动 AI 链接到新分类
    """
    await collection.update_many(
        {"_id": {"$in": [ObjectId(i) for i in ids]}},
        {"$set": {"category_id": new_category_id}}
    )


async def query_ai_link_by_id(collection: AsyncIOMotorCollection,
                             _id: str):
    """
    挑选目录根据 _id 查询单个 AI 链接
    """
    doc = await collection.find_one({"_id": ObjectId(_id)})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


async def query_ai_link_by_name(collection: AsyncIOMotorCollection, name: str, category_id: str):
    """
    根据名称和分类 ID 查询单个 AI 链接（用于查重）
    """
    doc = await collection.find_one({"name": name, "category_id": category_id})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


async def query_ai_links_by_filter(collection: AsyncIOMotorCollection, filter_query: dict):
    """
    通用过滤查询 (在此处统一处理 ObjectId 转换)
    """
    query = filter_query.copy() if filter_query else {}
    if "_id" in query and isinstance(query["_id"], str) and len(query["_id"]) == 24:
        try:
            from bson import ObjectId
            query["_id"] = ObjectId(query["_id"])
        except Exception:
            pass

    cursor = collection.find(query).sort('order', 1)
    ls = []
    async for doc in cursor:
        doc['_id'] = str(doc['_id'])
        ls.append(doc)
    return ls
