# src/ai_experience/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Union, Any, Dict
from fastapi import UploadFile, Form
from enum import Enum

class ExperienceType(str, Enum):
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    CHAT = "chat"
    TEXT_TO_AUDIO = "text_to_audio" # 预留
    TEXT_TO_VIDEO = "text_to_video" # 预留

# --- 具体的 Payload 定义 (与 AI 接口参数对应) ---

class TextToImageConfig(BaseModel):
    prompt: str
    aspect_ratio: Optional[str] = "1:1"

class ImageToImageConfig(BaseModel):
    prompt: str
    ref_images: List[str] # 预设参考图 URL 列表

class ChatConfig(BaseModel):
    system_prompt: str
    first_prompt: Optional[str] = None

# --- CRUD 模型 ---

class AIExperienceBase(BaseModel):
    title: str
    description: Optional[str] = None
    experience_type: ExperienceType
    default_prompt: str  # 必填，存放核心提示词（Prompt / System Prompt）
    cover_url: Optional[str] = None # 案例封面图 URL
    config: Dict[str, Any] = {} # 存放额外参数（如图生图的参考图链接）
    tags: List[str] = []
    order: int = 0

class AIExperienceCreateBody(BaseModel):
    """
    用于 Router 接收 Form 表单数据
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str = Form(...)
    description: Optional[str] = Form(None)
    experience_type: ExperienceType = Form(...)
    default_prompt: str = Form(...) # 改为必填的提示词字段
    preview_image: Optional[UploadFile] = None
    ref_images_files: Optional[List[UploadFile]] = None

class AIExperienceResponse(AIExperienceBase):
    mongo_id: str = Field(alias="_id")
    title: str
    description: Optional[str] = None
    experience_type: ExperienceType
    default_prompt: str
    cover_url: Optional[str] = None
    config: Dict[str, Any] = {}
    tags: List[str] = []
    order: int = 0

class AIExperienceUpdateBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    mongo_id: str = Form(...)
    title: Optional[str] = Form(None)
    description: Optional[str] = Form(None)
    experience_type: Optional[ExperienceType] = Form(None)
    default_prompt: Optional[str] = Form(None)
    preview_image: Optional[UploadFile] = None
    ref_images_files: Optional[List[UploadFile]] = None
    order: Optional[int] = Form(None)

class AIExperienceBatchDeleteRequest(BaseModel):
    ids: List[str]
