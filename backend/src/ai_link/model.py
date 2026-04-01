# src/ai_link/model.py

from . import schemas as ai_link_schemas
from src.database.mongodb import db
from src.database import ai_link_repo, category_repo
from fastapi import HTTPException, UploadFile
from src.utils import tool


AIHubCollection = db['AIHub']
CategoryCollection = db['Category']


async def upload_icon(file: UploadFile):
    """
    挑选目录处理图标上传业务逻辑
    """
    icon_url = await tool.save_upload_file(
        file = file,
        destination_dir = "static/icons"
    )
    return icon_url


# --- AI Link Services Logic ---

async def get_ai_links(category_id: str = None):
    """
    挑选目录获取 AI 链接（支持按分类 ID 筛选）
    """
    res = await ai_link_repo.query_ai_links(AIHubCollection, category_id)
    return res


async def get_grouped_ai_hub():
    """
    获取分组后的 AI 应用：按 Category 排序，每个 Category 下包含其 AI 链接
    """
    categories = await category_repo.query_categories(CategoryCollection)
    
    result = []
    for category in categories:
        # 获取该分类下的所有链接
        links = await get_ai_links(str(category['_id']))
        result.append({
            "category": category,
            "items": links
        })
    
    return result


async def add_ai_link(ai_data: ai_link_schemas.AILinkAddRequestBody):
    """
    挑选目录向数据库添加新的 AI 链接
    """
    # 验证分类是否存在
    category = await category_repo.query_category_by_id(CategoryCollection, ai_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 获取当前分类下最大的 order
    max_order = await ai_link_repo.query_max_order(AIHubCollection, {"category_id": ai_data.category_id})

    # 构造文档
    new_doc = ai_data.model_dump()
    new_doc['order'] = max_order + 1

    # 存储到数据库
    await ai_link_repo.insert_ai_link(AIHubCollection, new_doc)

    return 'AI Link added successfully'


async def swap_ai_links_order(id_1: str, id_2: str):
    """
    交换两个 AI 链接的顺序
    """
    link1 = await ai_link_repo.query_ai_link_by_id(AIHubCollection, id_1)
    link2 = await ai_link_repo.query_ai_link_by_id(AIHubCollection, id_2)
    
    if not link1 or not link2:
        raise HTTPException(status_code=404, detail="AI Link not found")
    
    order1 = link1.get('order', 0)
    order2 = link2.get('order', 0)
    
    await ai_link_repo.update_item_order(AIHubCollection, id_1, order2)
    await ai_link_repo.update_item_order(AIHubCollection, id_2, order1)
    
    return "Order swapped successfully"


async def delete_ai_link(ai_id: str):
    """
    挑选目录根据 _id 删除 AI 链接，并同步删除本地图标文件
    """
    # 1. 先查出该链接的信息，获取 icon_url
    ai_link = await ai_link_repo.query_ai_link_by_id(AIHubCollection, ai_id)
    if not ai_link:
        raise HTTPException(status_code=404, detail="AI Link not found")

    # 2. 从数据库删除记录
    success = await ai_link_repo.delete_ai_link(AIHubCollection, ai_id)

    if success:
        # 3. 数据库删除成功后，物理删除本地文件
        icon_url = ai_link.get('icon_url')
        if icon_url:
            tool.delete_local_file(icon_url)
        return 'AI Link deleted successfully'
    else:
        raise HTTPException(status_code=500, detail="Failed to delete database record")

