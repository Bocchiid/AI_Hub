# src/database/ai_hub_repo.py

from motor.motor_asyncio import AsyncIOMotorCollection


async def query_ai_links(collection: AsyncIOMotorCollection, 
                           category: str = None):
    """
    查询 AIHub 集合中的 AI 外部链接
    category: 可选的分类筛选
    """

    query_doc = {}
    if category:
        query_doc['category'] = category

    # 按 id 升序排序 (1 表示升序, -1 表示降序)
    cursor = collection.find(query_doc).sort('id', 1)
    ls = await cursor.to_list()

    return ls
