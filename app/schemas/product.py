from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ProductStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ProductBase(BaseModel):
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    currency: str = "USD"
    category_id: Optional[UUID] = None
    file_path: str = Field(..., max_length=500)
    file_name: str = Field(..., max_length=255)
    file_size: Optional[int] = None
    file_mime_type: Optional[str] = Field(None, max_length=100)
    download_limit: int = 5
    is_downloadable: bool = True
    status: ProductStatusEnum = ProductStatusEnum.DRAFT
    is_featured: bool = False
    is_active: bool = True
    preview_images: Optional[List[str]] = None
    preview_video: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    category_id: Optional[UUID] = None
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = None
    file_mime_type: Optional[str] = Field(None, max_length=100)
    download_limit: Optional[int] = None
    is_downloadable: Optional[bool] = None
    status: Optional[ProductStatusEnum] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    preview_images: Optional[List[str]] = None
    preview_video: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None


class ShowProduct(ProductBase):
    id: UUID
    seller_id: UUID
    views_count: int
    purchases_count: int
    rating_avg: float
    rating_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True