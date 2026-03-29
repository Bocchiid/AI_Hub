# src/ai_hub/schemas.py

from pydantic import BaseModel
from typing import List, Optional


class AIExternalLink(BaseModel):
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
