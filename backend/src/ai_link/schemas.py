# src/ai_link/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from src.category.schemas import Category
from fastapi import UploadFile

# --- Base Models ---

class AILink(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    mongo_id: str = Field(alias="_id")
    name: str
    icon_url: str
    external_url: str
    description: Optional[str] = None
    category_id: str
    order: int = 0


class AIHubGroup(BaseModel):
    category: Category
    items: List[AILink]


# --- Requests ---

class AILinkAddBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    icon: Optional[UploadFile] = None
    external_url: str
    description: Optional[str] = None
    category_name: Optional[str] = "默认分类"


class AILinkAddRequest(BaseModel):
    name: str
    icon_url: Optional[str] = None
    external_url: str
    description: Optional[str] = None
    category_id: str


class AILinkDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")


class AILinkUpdateBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    name: Optional[str] = None
    icon: Optional[UploadFile] = None
    external_url: Optional[str] = None
    description: Optional[str] = None
    category_name: Optional[str] = None


class AILinkUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    name: Optional[str] = None
    icon_url: Optional[str] = None
    external_url: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None


class AILinkQueryRequest(BaseModel):
    pass


class AILinkNameQueryRequest(AILinkQueryRequest):
    name: str


class AILinkIdQueryRequest(AILinkQueryRequest):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")


class AILinkReorderRequest(BaseModel):
    id_1: str
    id_2: str


class AILinkBatchDeleteRequest(BaseModel):
    mongo_ids: List[str] = Field(alias="mongo_ids")


class AILinkBatchMoveRequest(BaseModel):
    link_ids: List[str]
    new_category_id: str


class AIHubQueryRequest(BaseModel):
    pass


class AIHubsQueryRequest(BaseModel):
    pass


# --- Responses ---

class MsgResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message: str


class AILinkAddResponse(MsgResponse):
    pass


class AILinkDeleteResponse(MsgResponse):
    pass


class AILinkUpdateResponse(MsgResponse):
    pass


class AILinkQueryResponse(MsgResponse):
    items: List[AILink] = []


class AILinkNameQueryResponse(AILinkQueryResponse):
    pass


class AILinkIdQueryResponse(AILinkQueryResponse):
    pass


class AILinkReorderResponse(MsgResponse):
    pass


class AILinkBatchDeleteResponse(MsgResponse):
    pass


class AILinkBatchMoveResponse(MsgResponse):
    pass


class AIHubQueryResponse(MsgResponse):
    ai_hub_group: AIHubGroup


class AIHubsQueryResponse(MsgResponse):
    ai_hubs_groups: List[AIHubGroup] = []
