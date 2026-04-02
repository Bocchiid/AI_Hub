# src/category/model.py

from . import schemas as category_schemas
from src.database.mongodb import db
from src.database import category_repo
from src.utils import tool
from fastapi import HTTPException
from bson import ObjectId

# --- Base Configuration ---
CategoryCollection = db['Category']
AIHubCollection = db['AIHub']


async def add_category(category_request: category_schemas.CategoryCreateRequest):
    """
    添加新分类 (逻辑解耦：由 Router 预先处理好 icon_url)
    """
    # 0. 查重
    existing = await category_repo.query_category_by_name(CategoryCollection, category_request.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")

    # 1. 获取最大排序
    max_order = await category_repo.query_max_order(CategoryCollection)
    
    # 2. 组装完整文档
    new_category_document = category_request.model_dump()
    new_category_document['order'] = max_order + 1
    
    await category_repo.insert_category(CategoryCollection, new_category_document)
    return 'Category added successfully'


async def delete_category(category_id: str):
    """
    根据 _id 删除分类，并将子项移动到 Default 分类，同时删除磁盘上的图标文件
    """
    return await batch_delete_categories([category_id])


async def update_category(category_id: str, update_data: dict):
    """
    更新分类信息
    """
    # 过滤掉 None 值，只更新有值的字段
    filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
    if not filtered_update_data:
        return "No fields to update"

    # 1. 查重
    new_name = filtered_update_data.get("name")
    if new_name:
        existing = await category_repo.query_category_by_name(CategoryCollection, new_name)
        if existing and str(existing["_id"]) != category_id:
            raise HTTPException(status_code=400, detail="Category name already exists")
    
    await category_repo.update_category(CategoryCollection, category_id, filtered_update_data)
    return "Category updated successfully"


async def get_categories(filter_query: dict = None):
    """
    通用查询分类
    """
    # 如果 filter_query 中包含 mongo_id 或 _id，且是字符串，则转换为 ObjectId
    if filter_query:
        if "mongo_id" in filter_query:
            filter_query["_id"] = ObjectId(filter_query.pop("mongo_id"))
        elif "_id" in filter_query and isinstance(filter_query["_id"], str):
            filter_query["_id"] = ObjectId(filter_query["_id"])
            
    return await category_repo.query_categories(CategoryCollection, filter_query)


async def swap_categories_order(id_1: str, id_2: str):
    """
    交换两个分类的顺序
    """
    category1 = await category_repo.query_category(CategoryCollection, {"_id": ObjectId(id_1)})
    category2 = await category_repo.query_category(CategoryCollection, {"_id": ObjectId(id_2)})
    
    if not category1 or not category2:
        raise HTTPException(status_code=404, detail="Category not found")
    
    order1 = category1.get('order', 0)
    order2 = category2.get('order', 0)
    
    await category_repo.update_item_order(CategoryCollection, id_1, order2)
    await category_repo.update_item_order(CategoryCollection, id_2, order1)
    
    return "Category order swapped successfully"


async def init_default_category():
    """
    检查并初始化 Default 分类 (供系统启动时调用)
    """
    # 0. 为 name 字段建立唯一索引 (应对高并发并强制数据完整性)
    await CategoryCollection.create_index("name", unique=True)
    
    default_category = await category_repo.query_category(CategoryCollection, {"name": "默认分类"})
    if not default_category:
        max_order = await category_repo.query_max_order(CategoryCollection)
        new_category_document = {
            "name": "默认分类",
            "description": "默认分类",
            "order": max_order + 1,
            "icon_url": None
        }
        await category_repo.insert_category(CategoryCollection, new_category_document)
        return True
    return False


async def batch_delete_categories(category_ids: list[str]):
     # 1. 一次性查出所有要删除的分类（用于获取图标路径和验证）
    # 使用 $in 操作符
    target_categories = await category_repo.query_categories(
        CategoryCollection, 
        {"_id": {"$in": [ObjectId(i) for i in category_ids]}}
    )
    
    if len(target_categories) != len(category_ids):
        raise HTTPException(status_code=404, detail="One or more categories not found")

    # 2. 安全检查：排除“默认分类”
    for cat in target_categories:
        if cat.get('name') == "默认分类":
            raise HTTPException(status_code=400, detail="Cannot delete Default category")

    # 3. 获取“默认分类”的 ID（只需查一次）
    default_category = await category_repo.query_category(CategoryCollection, {"name": "默认分类"})
    if not default_category:
        raise HTTPException(status_code=500, detail="Default category not initialized")
    default_id = str(default_category['_id'])

    # 4. 执行批量转移应用
    await category_repo.move_ai_links_batch(AIHubCollection, category_ids, default_id)

    # 5. 批量物理删除磁盘图标
    for cat in target_categories:
        icon_url = cat.get("icon_url")
        if icon_url:
            tool.remove_file(icon_url)

    # 6. 批量删除分类记录
    await category_repo.delete_categories(CategoryCollection, category_ids)

    return f"Successfully deleted {len(category_ids)} categories"