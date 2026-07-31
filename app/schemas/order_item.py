from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class OrderItemBase(BaseModel):
    product_title: str = Field(..., max_length=255)
    product_price: float = Field(..., gt=0)
    product_file_path: str = Field(..., max_length=500)
    product_file_name: str = Field(..., max_length=255)
    quantity: int = 1
    subtotal: float = Field(..., gt=0)


class OrderItemCreate(BaseModel):
    product_id: UUID = Field(..., description="ID продукта")
    quantity: int = Field(1, ge=1, description="Количество")


class ShowOrderItem(OrderItemBase):
    id: UUID
    order_id: UUID
    product_id: UUID
    download_count: int
    last_download_at: Optional[datetime] = None 
    created_at: datetime

    class Config:
        from_attributes = True