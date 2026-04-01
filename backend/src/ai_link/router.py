# src/ai_link/router.py

from fastapi import APIRouter, File, UploadFile, Depends
from . import schemas as ai_link_schemas
from . import model as ai_link_model
from src.utils import auth
from typing import Optional

router = APIRouter(
    prefix="/ai_link",
    tags=["AI Link"]
)

@router.get("/all", response_model=ai_link_schemas.AIHubGroupResponse)
async def get_all_ai_apps():
    """
    获取分组展示的所有 AI 应用（按分类分组）
    """
    grouped_data = await ai_link_model.get_grouped_ai_hub()
    return ai_link_schemas.AIHubGroupResponse(groups=grouped_data)

@router.get("/{category_id}", response_model=ai_link_schemas.AIHubResponse)
async def get_ai_apps_by_category(category_id: str):
    """
    根据分类获取 AI 应用
    """
    ai_apps = await ai_link_model.get_ai_links(category_id)
    return ai_link_schemas.AIHubResponse(items=ai_apps)

@router.post("/add", response_model=ai_link_schemas.AILinkAddResponse, dependencies=[Depends(auth.admin_required)])
async def add_new_ai_hub(ai_add_request_body: ai_link_schemas.AILinkAddRequestBody):
    """
    添加新的 AI 外部链接 (仅限管理员)
    """
    res = await ai_link_model.add_ai_link(ai_add_request_body)
    return ai_link_schemas.AILinkAddResponse(message=res)

@router.post("/reorder", response_model=ai_link_schemas.AILinkReorderResponse, dependencies=[Depends(auth.admin_required)])
async def swap_ai_link_order(swap_req: ai_link_schemas.AILinkReorderRequest):
    """
    交换两个 AI 链接的顺序 (仅管理员)
    """
    res = await ai_link_model.swap_ai_links_order(swap_req.id_1, swap_req.id_2)
    return ai_link_schemas.AILinkReorderResponse(message=res)

@router.post("/icon/upload", response_model=ai_link_schemas.AIIconUploadResponse, dependencies=[Depends(auth.admin_required)])
async def upload_ai_icon(file: UploadFile = File(...)):
    """
    上传 AI 图标文件 (仅限管理员)
    """
    icon_url = await ai_link_model.upload_icon(file)
    return ai_link_schemas.AIIconUploadResponse(icon_url=icon_url)

@router.delete("/{ai_id}", response_model=ai_link_schemas.AILinkDeleteResponse, dependencies=[Depends(auth.admin_required)])
async def delete_ai_hub(ai_id: str):
    """
    根据 _id 删除指定的 AI 链接 (仅限管理员)
    """
    res = await ai_link_model.delete_ai_link(ai_id)
    return ai_link_schemas.AILinkDeleteResponse(message=res)

