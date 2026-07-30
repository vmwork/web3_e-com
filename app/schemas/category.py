from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    icon: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=7)
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    icon: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=7)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ShowCategory(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True