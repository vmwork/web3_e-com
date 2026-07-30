import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DownloadTokenBase(BaseModel):
    token: str = Field(..., max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    expires_at: datetime


class DownloadTokenCreate(DownloadTokenBase):
    order_item_id: uuid.UUID


class ShowDownloadToken(DownloadTokenBase):
    id: uuid.UUID
    order_item_id: uuid.UUID
    used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True