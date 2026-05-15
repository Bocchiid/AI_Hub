# src/doubao/schemas.py

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


class ChatRequestBody(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None


class ChatRequest(BaseModel):
    prompt: str
    user_id: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None

    class Config:
        from_attributes = True


class ChatHistoryListQuery(BaseModel):
    user_id: str


class ChatHistorySummary(BaseModel):
    title: str
    conversation_id: str


class ChatHistoryListResponse(BaseModel):
    chat_history_list: List[ChatHistorySummary]

    class Config:
        from_attributes = True


class ChatHistoryQuery(BaseModel):
    user_id: str
    conversation_id: str


class ChatHistoryResponse(BaseModel):
    title: str
    chat_history: List[Dict[str, str]]

    class Config:
        from_attributes = True


class PromptToImageRequestBody(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None


class PromptToImageRequest(BaseModel):
    prompt: str
    user_id: str
    conversation_id: Optional[str] = None


class PromptToImageResponse(BaseModel):
    img_urls: List[str]
    conversation_id: Optional[str] = None

    class Config:
        from_attributes = True


class ImageToImageRequestBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    prompt: str = Form(...)
    images: List[UploadFile] = File(...)
    conversation_id: Optional[str] = Form(None)


class ImageToImageRequest(BaseModel):
    prompt: str
    images: List[str] # 这里的 images 存储的是上传文件的 Base64 字符串
    user_id: str
    conversation_id: Optional[str] = None


class ImageToImageResponse(BaseModel):
    img_urls: List[str]
    conversation_id: Optional[str] = None

    class Config:
        from_attributes = True