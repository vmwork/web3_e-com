import enum
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from utils.uuid_utils import generate_uuid7


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid7, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    
    buyer_email = Column(String(255), nullable=True)
    buyer_wallet = Column(String(100), nullable=False)
    
    payment_method = Column(String(50), nullable=True)
    payment_tx_hash = Column(String(255), nullable=True)
    payment_currency = Column(String(10), nullable=True)
    payment_amount = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_orders_buyer_status', 'buyer_id', 'status'),
        Index('ix_orders_created_at', 'created_at'),
        Index('ix_orders_status', 'status'),
    )