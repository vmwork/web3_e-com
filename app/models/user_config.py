from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from utils.uuid_utils import generate_uuid7


class UserConfig(Base):
    __tablename__ = "user_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid7, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String, default="system")
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    notifications = Column(JSON, nullable=True)
    privacy = Column(JSON, nullable=True)
    preferences = Column(JSON, nullable=True)
    additional_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="config")