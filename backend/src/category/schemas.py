# src/category/schemas.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from fastapi import UploadFile


# --- Base Models ---

class Category(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    name: str
    icon_url: Optional[str] = None
    description: Optional[str] = None
    order: int = 0


# --- Requests ---

class CategoryCreateBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    icon: Optional[UploadFile] = None
    description: Optional[str] = None


class CategoryCreateRequest(BaseModel):
    name: str
    icon_url: Optional[str] = None
    description: Optional[str] = None


class CategoryDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")


class CategoryUpdateBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    name: Optional[str] = None
    icon: Optional[UploadFile] = None
    description: Optional[str] = None


class CategoryUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")
    name: Optional[str] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None


class CategoryQueryRequest(BaseModel):
    pass


class CategoryNameQueryRequest(CategoryQueryRequest):
    name: str


class CategoryIdQueryRequest(CategoryQueryRequest):
    model_config = ConfigDict(populate_by_name=True)

    mongo_id: str = Field(alias="_id")


class CategoryReorderRequest(BaseModel):
    id_1: str
    id_2: str


# --- Responses ---

class MsgResponse(BaseModel):
    message: str


class CategoryCreateResponse(MsgResponse):
    pass


class CategoryDeleteResponse(MsgResponse):
    pass


class CategoryUpdateResponse(MsgResponse):
    pass


class CategoryQueryResponse(MsgResponse):
    categories: List[Category] = []

    class Config:
        from_attributes = True


class CategoryNameQueryResponse(CategoryQueryResponse):
    pass


class CategoryIdQueryResponse(CategoryQueryResponse):
    pass


class CategoryReorderResponse(MsgResponse):
    pass  