from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from utils.uuid_utils import generate_uuid7


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid7, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    product_title = Column(String(255), nullable=False)
    product_price = Column(Float, nullable=False)
    product_file_path = Column(String(500), nullable=False)
    product_file_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    subtotal = Column(Float, nullable=False)
    
    download_count = Column(Integer, default=0)
    last_download_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    download_tokens = relationship("DownloadToken", back_populates="order_item", cascade="all, delete-orphan")