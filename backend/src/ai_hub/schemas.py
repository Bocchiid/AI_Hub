# src/ai_hub/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class AIExternalLink(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    id: str
    name: str
    icon_url: str
    external_url: str
    description: Optional[str] = None
    category: Optional[str] = "Chat"


class AIHubResponse(BaseModel):
    items: List[AIExternalLink]

    class Config:
        from_attributes = True


class AIAddRequestBody(BaseModel):
    name: str
    icon_url: str
    external_url: str
    description: Optional[str] = None
    category: Optional[str] = "Chat"


class AIAddRequest(AIAddRequestBody):
    id: str


class AIDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    mongo_id: str = Field(alias="_id")


class AIAddResponse(BaseModel):
    message: str


class AIDeleteResponse(BaseModel):
    message: str


class AIIconUploadResponse(BaseModel):
    icon_url: str

    class Config:
        from_attributes = True