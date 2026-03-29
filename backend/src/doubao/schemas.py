# src/doubao/schemas.py

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


class ChatGenerateImageRequestBody(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None


class ChatGenerateImageRequest(BaseModel):
    prompt: str
    user_id: str
    conversation_id: Optional[str] = None


class ChatGenerateImageResponse(BaseModel):
    img_url: str
    conversation_id: Optional[str] = None

    class Config:
        from_attributes = True