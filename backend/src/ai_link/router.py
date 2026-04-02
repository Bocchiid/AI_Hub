# src/ai_link/router.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from . import schemas as ai_link_schemas
from . import model as ai_link_model
from src.category.model import get_categories
from src.utils.auth import admin_required
from src.utils import tool

router = APIRouter(
    tags=["AI Link"]
)


@router.post("/add", response_model=ai_link_schemas.AILinkAddResponse, dependencies=[Depends(admin_required)])
async def add_ai_link(
    body: ai_link_schemas.AILinkAddBody = Depends()
):
    """
    添加新 AI 链接 (仅管理员)
    """
    # 1. 查找分类 ID
    category = await get_categories({"name": body.category_name})
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{body.category_name}' not found")
    category_id = str(category[0]["_id"])

    # 2. 处理文件
    icon_url = None
    if body.icon:
        if not body.icon.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        icon_url = await tool.upload_file(body.icon, sub_dir="ai_link/icons")

    # 3. 调用 Model
    request_data = ai_link_schemas.AILinkAddRequest(
        name=body.name,
        icon_url=icon_url,
        external_url=body.external_url,
        description=body.description,
        category_id=category_id
    )
    message = await ai_link_model.add_ai_link(request_data)
    return ai_link_schemas.AILinkAddResponse(message=message)


@router.post("/delete", response_model=ai_link_schemas.AILinkDeleteResponse, dependencies=[Depends(admin_required)])
async def delete_ai_link(req: ai_link_schemas.AILinkDeleteRequest):
    """
    删除单个 AI 链接
    """
    message = await ai_link_model.delete_ai_link(req.mongo_id)
    return ai_link_schemas.AILinkDeleteResponse(message=message)


@router.post("/update", response_model=ai_link_schemas.AILinkUpdateResponse, dependencies=[Depends(admin_required)])
async def update_ai_link(
    body: ai_link_schemas.AILinkUpdateBody = Depends()
):
    """
    更新 AI 链接
    """
    # 1. 处理分类名称转 ID
    category_id = None
    if body.category_name:
        category = await get_categories({"name": body.category_name})
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{body.category_name}' not found")
        category_id = str(category[0]["_id"])

    # 2. 处理图标
    icon_url = None
    if body.icon:
        icon_url = await tool.upload_file(body.icon, sub_dir="ai_link/icons")
        # 清理旧图标
        old_item = await ai_link_model.get_ai_links({"_id": body.mongo_id})
        if old_item and old_item[0].get("icon_url"):
            tool.remove_file(old_item[0]["icon_url"])

    # 3. 构建更新数据
    update_data = body.model_dump(exclude={"mongo_id", "icon", "category_name"}, exclude_none=True)
    if icon_url:
        update_data["icon_url"] = icon_url
    if category_id:
        update_data["category_id"] = category_id

    message = await ai_link_model.update_ai_link(body.mongo_id, update_data)
    return ai_link_schemas.AILinkUpdateResponse(message=message)


@router.post("/reorder", response_model=ai_link_schemas.AILinkReorderResponse, dependencies=[Depends(admin_required)])
async def reorder_ai_links(req: ai_link_schemas.AILinkReorderRequest):
    message = await ai_link_model.swap_ai_links_order(req.id_1, req.id_2)
    return ai_link_schemas.AILinkReorderResponse(message=message)


@router.get("/query", response_model=ai_link_schemas.AILinkQueryResponse)
async def get_all_ai_links():
    items = await ai_link_model.get_ai_links()
    return ai_link_schemas.AILinkQueryResponse(message="Success", items=items)


@router.get("/query/id/{id}", response_model=ai_link_schemas.AILinkIdQueryResponse)
async def get_ai_link_by_id(id: str):
    """
    根据 ID 查询单个 AI 链接
    """
    items = await ai_link_model.get_ai_links({"_id": id})
    if not items:
        raise HTTPException(status_code=404, detail="AI Link not found")
    return ai_link_schemas.AILinkIdQueryResponse(message="Success", items=items)


@router.get("/query/name/{name}", response_model=ai_link_schemas.AILinkNameQueryResponse)
async def get_ai_link_by_name(name: str):
    items = await ai_link_model.get_ai_links({"name": name})
    return ai_link_schemas.AILinkNameQueryResponse(message="Success", items=items)


@router.post("/batch_delete", response_model=ai_link_schemas.AILinkBatchDeleteResponse, dependencies=[Depends(admin_required)])
async def batch_delete(req: ai_link_schemas.AILinkBatchDeleteRequest):
    message = await ai_link_model.batch_delete_ai_links(req.mongo_ids)
    return ai_link_schemas.AILinkBatchDeleteResponse(message=message)


@router.post("/batch_move", response_model=ai_link_schemas.AILinkBatchMoveResponse, dependencies=[Depends(admin_required)])
async def batch_move(req: ai_link_schemas.AILinkBatchMoveRequest):
    message = await ai_link_model.batch_move_ai_links(req.link_ids, req.new_category_id)
    return ai_link_schemas.AILinkBatchMoveResponse(message=message)


@router.get("/query/ai_hub/{category_id}", response_model=ai_link_schemas.AIHubQueryResponse)
async def get_ai_hub_by_category(category_id: str):
    """
    按分类 ID 获取单个 AI Hub 聚合数据 (分类信息 + 链接列表)
    """
    # 1. 获取分类信息
    category = await get_categories({"_id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")

    # 2. 获取该分类下的链接
    links = await ai_link_model.get_ai_links({"category_id": category_id})

    # 3. 组装响应
    hub_group = ai_link_schemas.AIHubGroup(
        category=category[0],
        items=links
    )
    return ai_link_schemas.AIHubQueryResponse(message="Success", ai_hub_group=hub_group)


@router.get("/query/ai_hubs", response_model=ai_link_schemas.AIHubsQueryResponse)
async def get_ai_hubs_grouped():
    """
    获取所有分类及其对应的 AI 链接聚合数据
    """
    data = await ai_link_model.get_ai_hubs()
    return ai_link_schemas.AIHubsQueryResponse(message="Success", ai_hubs_groups=data)
