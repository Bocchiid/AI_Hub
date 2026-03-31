# src/ai_hub/router.py

from fastapi import APIRouter, File, UploadFile, Depends
from . import schemas as ai_hub_schemas
from . import model as ai_hub_model
from src.utils import auth


from typing import Optional


router = APIRouter(
    tags = ["AI Hub"]
)


@router.get("/all", response_model = ai_hub_schemas.AIHubResponse)
async def get_all_ai_apps():
    """
    获取首页展示的所有 AI 应用
    """

    ai_apps = await ai_hub_model.get_ai_links()

    return ai_hub_schemas.AIHubResponse(
        items = [ai_hub_schemas.AIExternalLink(**app) for app in ai_apps]
    )


@router.get("/{category}", response_model = ai_hub_schemas.AIHubResponse)
async def get_ai_apps_by_category(category: str):
    """
    根据分类获取 AI 应用
    """

    ai_apps = await ai_hub_model.get_ai_links(category)

    return ai_hub_schemas.AIHubResponse(
        items = [ai_hub_schemas.AIExternalLink(**app) for app in ai_apps]
    )


@router.post("/add", response_model = ai_hub_schemas.AIAddResponse, dependencies=[Depends(auth.admin_required)])
async def add_new_ai_hub(ai_add_request_body: ai_hub_schemas.AIAddRequestBody):
    """
    添加新的 AI 外部链接 (仅限管理员)
    """

    res = await ai_hub_model.add_ai_link(ai_add_request_body)

    return ai_hub_schemas.AIAddResponse(
        message = res
    )


@router.post("/icon/upload", response_model = ai_hub_schemas.AIIconUploadResponse, dependencies=[Depends(auth.admin_required)])
async def upload_ai_icon(file: UploadFile = File(...)):
    """
    上传 AI 图标文件 (仅限管理员)
    """

    icon_url = await ai_hub_model.upload_icon(file)

    return ai_hub_schemas.AIIconUploadResponse(
        icon_url = icon_url
    )


@router.post("/delete", response_model = ai_hub_schemas.AIDeleteResponse, dependencies=[Depends(auth.admin_required)])
async def delete_ai_hub(delete_request: ai_hub_schemas.AIDeleteRequest):
    """
    根据 _id 删除指定的 AI 链接 (仅限管理员)
    """

    res = await ai_hub_model.delete_ai_link(delete_request.mongo_id)

    return ai_hub_schemas.AIDeleteResponse(
        message = res
    )
