# src/ai_hub/model.py

from . import schemas as ai_hub_schemas
from src.database.mongodb import db
from src.database import ai_hub_repo
from fastapi import HTTPException, UploadFile
from src.utils import tool


AIHubCollection = db['AIHub']


async def get_ai_links(category: str = None):
    """
    挑选目录获取 AI 链接（支持按分类筛选）
    """

    res = await ai_hub_repo.query_ai_links(AIHubCollection, category)

    return res


async def add_ai_link(ai_data: ai_hub_schemas.AIAddRequestBody):
    """
    挑选目录向数据库添加新的 AI 链接
    """

    # 1. 自动 ID 计算：获取当前最大 ID 并递增
    max_id_str = await ai_hub_repo.query_max_id(AIHubCollection)
    next_id = int(max_id_str) + 1

    # 2. 构造完整的 AIAddRequest
    ai_add_request = ai_hub_schemas.AIAddRequest(
        id = str(next_id),
        **ai_data.model_dump()
    )

    # 3. 存储到数据库
    new_doc = ai_add_request.model_dump()
    await ai_hub_repo.insert_ai_link(AIHubCollection, new_doc)

    return 'AI Link added successfully'


async def upload_icon(file: UploadFile):
    """
    挑选目录处理图标上传业务逻辑
    """
    icon_url = await tool.save_upload_file(
        file = file,
        destination_dir = "static/icons"
    )
    return icon_url


async def delete_ai_link(ai_id: str):
    """
    挑选目录根据 _id 删除 AI 链接，并同步删除本地图标文件
    """
    # 1. 先查出该链接的信息，获取 icon_url
    ai_link = await ai_hub_repo.query_ai_link_by_id(AIHubCollection, ai_id)
    if not ai_link:
        raise HTTPException(status_code=404, detail="AI Link not found")

    # 2. 从数据库删除记录
    success = await ai_hub_repo.delete_ai_link(AIHubCollection, ai_id)

    if success:
        # 3. 数据库删除成功后，物理删除本地文件
        icon_url = ai_link.get('icon_url')
        if icon_url:
            tool.delete_local_file(icon_url)
        return 'AI Link deleted successfully'
    else:
        raise HTTPException(status_code=500, detail="Failed to delete database record")
