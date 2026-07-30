import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    is_verified_purchase: bool = False
    is_approved: bool = False


class ReviewCreate(ReviewBase):
    product_id: uuid.UUID
    user_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    is_approved: Optional[bool] = None


class ShowReview(ReviewBase):
    id: uuid.UUID
    product_id: uuid.UUID
    user_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True