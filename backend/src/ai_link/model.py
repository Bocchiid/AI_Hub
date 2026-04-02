# src/ai_link/model.py

from . import schemas as ai_link_schemas
from src.database.mongodb import db
from src.database import ai_link_repo, category_repo
from src.utils import tool
from fastapi import HTTPException
from bson import ObjectId

# --- Base Configuration ---
AIHubCollection = db['AIHub']
CategoryCollection = db['Category']


async def add_ai_link(ai_request: ai_link_schemas.AILinkAddRequest):
    """
    添加新 AI 链接
    """
    # 0. 在该分类下查重
    existing = await ai_link_repo.query_ai_link_by_name(
        AIHubCollection, ai_request.name, ai_request.category_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="AI link name already exists in this category")

    # 1. 获取最大排序 (按分类)
    max_order = await ai_link_repo.query_max_order(AIHubCollection, {"category_id": ai_request.category_id})
    
    # 2. 组装文档
    new_ai_document = ai_request.model_dump()
    new_ai_document['order'] = max_order + 1
    
    await ai_link_repo.insert_ai_link(AIHubCollection, new_ai_document)
    return "AI link added successfully"


async def delete_ai_link(ai_id: str):
    """
    删除单个 AI 链接
    """
    return await batch_delete_ai_links([ai_id])


async def update_ai_link(ai_id: str, update_data: dict):
    """
    更新 AI 链接
    """
    filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
    if not filtered_update_data:
        return "No fields to update"

    # 1. 如果更新了名字或分类，需要重新查重
    target_ai = await ai_link_repo.query_ai_link_by_id(AIHubCollection, ai_id)
    if not target_ai:
        raise HTTPException(status_code=404, detail="AI link not found")

    new_name = filtered_update_data.get("name", target_ai["name"])
    new_cat_id = filtered_update_data.get("category_id", target_ai["category_id"])

    if "name" in filtered_update_data or "category_id" in filtered_update_data:
        existing = await ai_link_repo.query_ai_link_by_name(AIHubCollection, new_name, new_cat_id)
        if existing and str(existing["_id"]) != ai_id:
            raise HTTPException(status_code=400, detail="AI link name already exists in target category")

    await ai_link_repo.update_ai_link(AIHubCollection, ai_id, filtered_update_data)
    return "AI link updated successfully"


async def get_ai_links(filter_query: dict = None):
    """
    通用查询 AI 链接 (保持参数为原始字典/字符串)
    """
    if filter_query is None:
        filter_query = {}
    else:
        filter_query = filter_query.copy()

    # 兼容处理：将 mongo_id 统一转换为 _id 字符串
    if "mongo_id" in filter_query:
        filter_query["_id"] = filter_query.pop("mongo_id")
            
    return await ai_link_repo.query_ai_links_by_filter(AIHubCollection, filter_query)


async def swap_ai_links_order(id_1: str, id_2: str):
    """
    交换两个 AI 链接的顺序
    """
    ai1 = await ai_link_repo.query_ai_link_by_id(AIHubCollection, id_1)
    ai2 = await ai_link_repo.query_ai_link_by_id(AIHubCollection, id_2)
    
    if not ai1 or not ai2:
        raise HTTPException(status_code=404, detail="AI link not found")
    
    await ai_link_repo.update_item_order(AIHubCollection, id_1, ai2.get('order', 0))
    await ai_link_repo.update_item_order(AIHubCollection, id_2, ai1.get('order', 0))
    return "Order swapped successfully"


async def batch_delete_ai_links(ai_ids: list[str]):
    """
    批量删除 AI 链接 (包含图标下线)
    """
    # 1. 查找并删除物理图标
    target_links = await ai_link_repo.query_ai_links_by_filter(
        AIHubCollection, {"_id": {"$in": [ObjectId(i) for i in ai_ids]}}
    )
    for link in target_links:
        if link.get("icon_url"):
            tool.remove_file(link["icon_url"])

    # 2. 数据库删除
    await ai_link_repo.delete_ai_links_batch(AIHubCollection, ai_ids)
    return f"Successfully deleted {len(ai_ids)} AI links"


async def batch_move_ai_links(ai_ids: list[str], new_category_id: str):
    """
    批量移动 AI 链接
    """
    await ai_link_repo.batch_move_ai_links(AIHubCollection, ai_ids, new_category_id)
    return f"Successfully moved {len(ai_ids)} AI links"


async def get_ai_hubs():
    """
    获取 AI Hub 聚合数据 (分类 -> AI 列表)
    """
    # 1. 获取所有分类
    categories = await category_repo.query_categories(CategoryCollection)
    
    result = []
    for cat in categories:
        # 2. 获取该分类下所有 AI 链接
        links = await ai_link_repo.query_ai_links(AIHubCollection, str(cat["_id"]))
        result.append({
            "category": cat,
            "items": links
        })
    return result
