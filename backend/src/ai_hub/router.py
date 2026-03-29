# src/ai_hub/router.py

from fastapi import APIRouter
from . import schemas as ai_hub_schemas
from . import model as ai_hub_model


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
