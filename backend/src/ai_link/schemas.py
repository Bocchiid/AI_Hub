# src/ai_link/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from src.category.schemas import Category

# 1. 基础实体 (Base Models)

class AILink(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    name: str
    icon_url: str
    external_url: str
    description: Optional[str] = None
    category_id: str
    order: int = 0


class CategoryGroup(BaseModel):
    category: Category
    items: List[AILink]


# 2. 请求 (Requests)

# --- AI Link Schemas ---

class AILinkAddRequestBody(BaseModel):
    name: str
    icon_url: str
    external_url: str
    description: Optional[str] = None
    category_id: str


class AILinkReorderRequest(BaseModel):
    id_1: str
    id_2: str


# 3. 响应 (Responses)

class MsgResponse(BaseModel):
    message: str


# --- AI Link Responses ---

class AILinkAddResponse(MsgResponse):
    pass


class AILinkDeleteResponse(MsgResponse):
    pass


class AILinkReorderResponse(MsgResponse):
    pass


class AIHubGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    groups: List[CategoryGroup]


class AIHubResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AILink]


class AIIconUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    icon_url: str
