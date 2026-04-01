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


async def query_ai_link_by_id(collection: AsyncIOMotorCollection,
                             _id: str):
    """
    挑选目录根据 _id 查询单个 AI 链接
    """
    doc = await collection.find_one({"_id": ObjectId(_id)})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc
