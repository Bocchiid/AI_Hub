# src/doubao/schemas.py

from fastapi import Form
from pydantic import BaseModel
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
    prompt: str
    images: List[str]
    conversation_id: Optional[str] = None


class ImageToImageRequest(BaseModel):
    prompt: str
    images: List[str]
    user_id: str
    conversation_id: Optional[str] = None


class ImageToImageResponse(BaseModel):
    img_urls: List[str]
    conversation_id: Optional[str] = None

    class Config:
        from_attributes = True