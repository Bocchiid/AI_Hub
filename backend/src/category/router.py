# src/category/router.py

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from . import schemas as category_schemas
from . import model as category_model
from src.utils.auth import admin_required
from src.utils import tool

router = APIRouter(
    tags=["Category"]
)


@router.post("/add", response_model=category_schemas.CategoryCreateResponse, dependencies=[Depends(admin_required)])
async def add_category(
    category_body: category_schemas.CategoryCreateBody = Depends()
):
    """
    添加新分类 (仅管理员)
    """
    # 1. 在 Router 处理文件上传得到 URL
    icon_url = None
    if category_body.icon:
        if not category_body.icon.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        icon_url = await tool.upload_file(category_body.icon, sub_dir="category/icons")

    # 2. 封装为 CategoryCreateRequest 传给 model
    category_request = category_schemas.CategoryCreateRequest(
        name=category_body.name,
        icon_url=icon_url,
        description=category_body.description
    )
    
    # 3. 调用 Model
    message = await category_model.add_category(category_request)
    return category_schemas.CategoryCreateResponse(message=message)


@router.post("/delete", response_model=category_schemas.CategoryDeleteResponse, dependencies=[Depends(admin_required)])
async def delete_category(category_delete_request: category_schemas.CategoryDeleteRequest):
    """
    根据 _id 删除分类 (仅管理员)
    """
    message = await category_model.delete_category(category_delete_request.mongo_id)
    return category_schemas.CategoryDeleteResponse(message=message)


@router.post("/update", response_model=category_schemas.CategoryUpdateResponse, dependencies=[Depends(admin_required)])
async def update_category(
    category_body: category_schemas.CategoryUpdateBody = Depends()
):
    """
    根据 _id 更新分类 (仅管理员)
    """
    # 1. 如果有新图标上传，先处理文件
    icon_url = None
    if category_body.icon:
        if not category_body.icon.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        # 上传新图标
        icon_url = await tool.upload_file(category_body.icon, sub_dir="category/icons")
        
        # 尝试删除旧图标 (先查询旧数据)
        old_category = await category_model.get_categories({"_id": category_body.mongo_id})
        if old_category and old_category[0].get("icon_url"):
            tool.remove_file(old_category[0]["icon_url"])

    # 2. 构造更新字典 (排除 _id 和二进制 icon)
    update_data = category_body.model_dump(exclude={"mongo_id", "icon"}, exclude_none=True)
    
    # 3. 如果有新生成的 icon_url，加入更新字典
    if icon_url:
        update_data["icon_url"] = icon_url

    # 4. 调用 Model 执行数据库更新
    message = await category_model.update_category(category_body.mongo_id, update_data)
    return category_schemas.CategoryUpdateResponse(message=message)


@router.post("/reorder", response_model=category_schemas.CategoryReorderResponse, dependencies=[Depends(admin_required)])
async def reorder_categories(category_reorder_request: category_schemas.CategoryReorderRequest):
    """
    交换两个分类的顺序 (仅管理员)
    """
    message = await category_model.swap_categories_order(
        category_reorder_request.id_1, 
        category_reorder_request.id_2
    )
    return category_schemas.CategoryReorderResponse(message=message)


@router.get("/query", response_model=category_schemas.CategoryQueryResponse)
async def get_all_categories():
    """
    获取全部分类列表
    """
    categories = await category_model.get_categories()
    return category_schemas.CategoryQueryResponse(
        message="Success",
        categories=categories
    )


@router.get("/query/id/{category_id}", response_model=category_schemas.CategoryIdQueryResponse)
async def get_category_by_id(category_id: str):
    """
    根据 _id 获取分类详情
    """
    categories = await category_model.get_categories({"_id": category_id})
    if not categories:
        return category_schemas.CategoryIdQueryResponse(message="Category not found", categories=[])
        
    return category_schemas.CategoryIdQueryResponse(
        message="Success",
        categories=categories
    )


@router.get("/query/name/{category_name}", response_model=category_schemas.CategoryNameQueryResponse)
async def get_category_by_name(category_name: str):
    """
    根据名称获取分类详情
    """
    categories = await category_model.get_categories({"name": category_name})
    if not categories:
        return category_schemas.CategoryNameQueryResponse(message="Category not found", categories=[])
    
    return category_schemas.CategoryNameQueryResponse(
        message="Success",
        categories=categories
    )
