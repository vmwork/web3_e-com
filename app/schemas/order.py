from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class OrderBase(BaseModel):
    order_number: str = Field(..., max_length=50)
    subtotal: float = Field(..., gt=0)
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    total_amount: float = Field(..., gt=0)
    currency: str = "USD"
    status: OrderStatusEnum = OrderStatusEnum.PENDING
    buyer_email: Optional[str] = Field(None, max_length=255)
    buyer_wallet: str = Field(..., max_length=100)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_tx_hash: Optional[str] = Field(None, max_length=255)
    payment_currency: Optional[str] = Field(None, max_length=10)
    payment_amount: Optional[float] = None


class OrderCreate(OrderBase):
    buyer_id: UUID
    items: List["OrderItemCreate"] = []  # строка


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_tx_hash: Optional[str] = Field(None, max_length=255)
    paid_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ShowOrder(OrderBase):
    id: UUID
    buyer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None 
    paid_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items: Optional[List["ShowOrderItem"]] = None  # строка

    class Config:
        from_attributes = True


from schemas.order_item import OrderItemCreate, ShowOrderItem
OrderCreate.model_rebuild()
ShowOrder.model_rebuild()