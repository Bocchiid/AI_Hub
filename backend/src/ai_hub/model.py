# src/ai_hub/model.py

from src.database import ai_hub_repo
from src.database.mongodb import db


AIHubCollection = db['AIHub']


async def get_ai_links(category: str = None):
    """
    业务逻辑：从数据库获取 AI 链接（支持按分类筛选）
    """

    res = await ai_hub_repo.query_ai_links(AIHubCollection, category)

    return res
