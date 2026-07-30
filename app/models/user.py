import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING = "pending"
    DANGER = "danger"

class User(Base):
    __tablename__ = "users"

    wallet_address = Column(String(100), primary_key=True, index=True, unique=True, nullable=False)
    wallet_type = Column(String(20), default="EVM")
    has_paid_entrance = Column(Boolean, default=False)
    paid_entrance_at = Column(DateTime, nullable=True)
    total_slots = Column(Integer, default=0)
    used_slots = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    total_deals = Column(Integer, default=0)
    positive_deals = Column(Integer, default=0)
    subscription_type = Column(String(20), default="free")
    subscription_until = Column(DateTime, nullable=True)
    fee_percent = Column(Integer, default=7)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    role = Column(String(20), default="user")
    display_name = Column(String(50), nullable=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), onupdate=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    config = relationship("UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
