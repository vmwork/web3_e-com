import enum
from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey, DateTime, JSON, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from utils.uuid_utils import generate_uuid7


class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid7, index=True)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_mime_type = Column(String(100), nullable=True)
    
    download_limit = Column(Integer, default=5)
    is_downloadable = Column(Boolean, default=True)
    
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    preview_images = Column(JSON, nullable=True)
    preview_video = Column(String(500), nullable=True)
    
    views_count = Column(Integer, default=0)
    purchases_count = Column(Integer, default=0)
    rating_avg = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    seller = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_products_status_price', 'status', 'price'),
        Index('ix_products_category_status', 'category_id', 'status'),
        Index('ix_products_created_at', 'created_at'),
    )