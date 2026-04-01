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
    # 1. 查询目标分类是否存在
    target_category = await category_repo.query_category(CategoryCollection, {"_id": ObjectId(category_id)})
    if not target_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 2. 禁止删除 Default 分类
    if target_category.get('name') == "Default":
        raise HTTPException(status_code=400, detail="Cannot delete Default category")

    # 3. 寻找或验证 Default 分类
    default_category = await category_repo.query_category(CategoryCollection, {"name": "Default"})
    if not default_category:
        raise HTTPException(status_code=500, detail="Default category not initialized")

    # 4. 执行批量转移应用
    await category_repo.move_ai_links_to_category(AIHubCollection, category_id, str(default_category['_id']))

    # 5. 删除物理磁盘上的图标文件
    icon_url = target_category.get("icon_url")
    if icon_url:
        tool.remove_file(icon_url)

    # 6. 删除数据库记录
    await category_repo.delete_category(CategoryCollection, category_id)

    return 'Category deleted and items moved to Default'


async def update_category(category_id: str, update_data: dict):
    """
    更新分类信息
    """
    # 过滤掉 None 值，只更新有值的字段
    filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
    if not filtered_update_data:
        return "No fields to update"
    
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
    default_category = await category_repo.query_category(CategoryCollection, {"name": "Default"})
    if not default_category:
        max_order = await category_repo.query_max_order(CategoryCollection)
        new_category_document = {
            "name": "Default",
            "description": "默认分类",
            "order": max_order + 1,
            "icon_url": None
        }
        await category_repo.insert_category(CategoryCollection, new_category_document)
        return True
    return False
