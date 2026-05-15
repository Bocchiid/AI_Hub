# src/ai_experience/router.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File
from fastapi.responses import StreamingResponse
from . import schemas as exp_schemas
from . import model as exp_model
from src.utils import tool
from src.utils.auth import admin_required, get_current_user
from src.doubao import model as doubao_model
from src.doubao import schemas as doubao_schemas
import json
import time
import base64
from typing import List, Optional

router = APIRouter(
    tags=["AI Experience"]
)

@router.post("/run")
async def run_experience(
    mongo_id: str = Form(...),
    user_images: List[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    运行体验案例 (无状态，不存历史)
    """
    # 1. 获取案例配置
    exp = await exp_model.get_experience_by_id(mongo_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    experience_type = exp.get("experience_type")

    # 2. 处理图片逻辑
    final_base64_list = []
    if user_images and user_images[0].size > 0:
        # 用户上传了新图片，直接转 Base64
        for img in user_images:
            content = await img.read()
            b64 = base64.b64encode(content).decode('utf-8')
            final_base64_list.append(b64)
    else:
        # 使用案例预设图
        config = exp.get("config", {})
        ref_images = config.get("ref_images", [])
        for url in ref_images:
            b64 = tool.file_to_base64(url)
            if b64:
                final_base64_list.append(b64)

    # 3. 调用 AI 核心逻辑 (save_history=False)
    if experience_type == exp_schemas.ExperienceType.IMAGE_TO_IMAGE:
        req = doubao_schemas.ImageToImageRequest(
            user_id=current_user["user_id"],
            prompt=exp["default_prompt"],
            images=final_base64_list,
            conversation_id=None
        )
        img_urls = await doubao_model.generate_image_to_image_response(req, save_history=False)
        return {"type": "image", "data": img_urls}
        
    elif experience_type == exp_schemas.ExperienceType.CHAT:
        req = doubao_schemas.ChatRequest(
            user_id=current_user["user_id"],
            prompt="你好，请开始吧", # 或者使用某个触发词
            conversation_id=None
        )
        # 如果是聊天类型，通常 default_prompt 是 system_prompt
        stream_gen, _ = await doubao_model.generate_stream_chat_response(
            req, 
            system_prompt=exp["default_prompt"], 
            save_history=False
        )
        return StreamingResponse(stream_gen, media_type="text/event-stream")

    return {"message": "Current experience type not supported for direct run"}

@router.post("/add", dependencies=[Depends(admin_required)])
async def add_ai_experience(
    body: exp_schemas.AIExperienceCreateBody = Depends()
):
    """
    添加 AI 体验案例 (仅管理员)
    """
    # 1. 核心提示词处理
    config = {}
    
    # 使用时间戳作为子目录，方便后续整文件夹删除
    timestamp = str(int(time.time()))
    experience_dir = f"experience/{timestamp}"

    # 2. 类型校验与图片接收控制
    if body.experience_type == exp_schemas.ExperienceType.IMAGE_TO_IMAGE:
        if not body.ref_images_files:
            raise HTTPException(status_code=400, detail="Image-to-Image 模式必须上传参考图")

    # 3. 处理封面图 (Cover Image)
    cover_url = None
    if body.preview_image:
        cover_url = await tool.upload_file(
            body.preview_image, 
            sub_dir=f"{experience_dir}/covers",
            allowed_types=["image/jpeg", "image/png", "image/webp"]
        )

    # 4. 处理参考图列表 (Presets)
    if body.ref_images_files:
        ref_image_urls = []
        for file in body.ref_images_files:
            url = await tool.upload_file(
                file, 
                sub_dir=f"{experience_dir}/presets",
                allowed_types=["image/jpeg", "image/png", "image/webp"]
            )
            ref_image_urls.append(url)
        config["ref_images"] = ref_image_urls
    
    config["storage_dir"] = experience_dir

    # 5. 构建存储数据
    save_data = {
        "title": body.title,
        "description": body.description,
        "experience_type": body.experience_type,
        "default_prompt": body.default_prompt,
        "config": config,
        "cover_url": cover_url,
        "tags": []
    }

    mongo_id = await exp_model.add_experience(save_data)
    return {"message": "Success", "id": mongo_id}

@router.post("/update", dependencies=[Depends(admin_required)])
async def update_ai_experience(
    body: exp_schemas.AIExperienceUpdateBody = Depends()
):
    """
    更新 AI 体验案例 (仅管理员)
    """
    # 1. 查询旧数据
    old_item = await exp_model.get_experience_by_id(body.mongo_id)
    if not old_item:
        raise HTTPException(status_code=404, detail="Experience not found")

    update_data = {}
    config = old_item.get("config", {})
    experience_dir = config.get("storage_dir")
    
    # 如果旧数据没有存储目录，生成一个（兼容旧数据）
    if not experience_dir:
        experience_dir = f"experience/{int(time.time())}"
        config["storage_dir"] = experience_dir

    # 2. 处理基本字段更新
    if body.title: update_data["title"] = body.title
    if body.description: update_data["description"] = body.description
    if body.experience_type: update_data["experience_type"] = body.experience_type
    if body.default_prompt: update_data["default_prompt"] = body.default_prompt
    if body.order is not None: update_data["order"] = body.order

    # 3. 处理图片更新
    if body.preview_image:
        if old_item.get("cover_url"):
            tool.remove_file(old_item["cover_url"])
        update_data["cover_url"] = await tool.upload_file(
            body.preview_image, 
            sub_dir=f"{experience_dir}/covers",
            allowed_types=["image/jpeg", "image/png", "image/webp"]
        )

    if body.ref_images_files:
        # 清理旧参考图
        if config.get("ref_images"):
            for url in config["ref_images"]:
                tool.remove_file(url)
        
        new_ref_urls = []
        for file in body.ref_images_files:
            url = await tool.upload_file(
                file, 
                sub_dir=f"{experience_dir}/presets",
                allowed_types=["image/jpeg", "image/png", "image/webp"]
            )
            new_ref_urls.append(url)
        config["ref_images"] = new_ref_urls

    update_data["config"] = config

    message = await exp_model.update_experience(body.mongo_id, update_data)
    return {"message": message}

@router.get("/list", response_model=List[exp_schemas.AIExperienceResponse])
async def list_ai_experiences(exp_type: Optional[exp_schemas.ExperienceType] = None):
    """
    获取体验案例列表 (支持按类型过滤)
    """
    query = {}
    if exp_type:
        query["experience_type"] = exp_type
    
    items = await exp_model.get_experiences(query)
    return items

@router.post("/delete", dependencies=[Depends(admin_required)])
async def delete_ai_experience(id: str = Form(...)):
    """
    删除案例 (仅管理员)
    """
    # 尝试查找并删除关联文件
    item = await exp_model.get_experience_by_id(id)
    if item:
        config = item.get("config", {})
        storage_dir = config.get("storage_dir")
        if storage_dir:
            tool.remove_directory(storage_dir)
        else:
            # 兼容旧逻辑
            if item.get("cover_url"):
                tool.remove_file(item["cover_url"])
            if config.get("ref_images"):
                for url in config["ref_images"]:
                    tool.remove_file(url)
    
    message = await exp_model.delete_experience(id)
    return {"message": message}

@router.post("/batch-delete", dependencies=[Depends(admin_required)])
async def batch_delete_ai_experiences(req: exp_schemas.AIExperienceBatchDeleteRequest):
    """
    批量删除案例 (仅管理员)
    """
    # 1. 循环处理文件清理
    for mongo_id in req.ids:
        item = await exp_model.get_experience_by_id(mongo_id)
        if item:
            config = item.get("config", {})
            storage_dir = config.get("storage_dir")
            if storage_dir:
                tool.remove_directory(storage_dir)
            else:
                if item.get("cover_url"):
                    tool.remove_file(item["cover_url"])
                if config.get("ref_images"):
                    for url in config["ref_images"]:
                        tool.remove_file(url)
    
    # 2. 执行数据库批量删除
    message = await exp_model.delete_many_experiences(req.ids)
    return {"message": message}
    return {"message": message}
