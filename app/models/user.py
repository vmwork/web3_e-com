# models/user.py
import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
from utils.uuid_utils import generate_uuid7


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING = "pending"
    DANGER = "danger"


class WalletType(str, enum.Enum):
    EVM = "EVM"
    SOLANA = "SOLANA"
    TRON = "TRON"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid7, index=True)
    
    # wallet_address теперь UNIQUE, но НЕ primary key
    wallet_address = Column(String(100), unique=True, nullable=True, index=True)
    wallet_type = Column(String(20), nullable=True)
    
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    is_email_verified = Column(Boolean, default=False)
    
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
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Связи теперь через user_id (UUID), а не wallet_address
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    config = relationship("UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    products = relationship("Product", back_populates="seller")
    orders = relationship("Order", back_populates="buyer")
    reviews = relationship("Review", back_populates="user")

    __table_args__ = (
        Index('ix_users_status_role', 'status', 'role'),
        Index('ix_users_subscription_until', 'subscription_until'),
    )