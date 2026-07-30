from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import os

from db.session import get_db
from models.user import User, UserStatus
from models.profile import Profile
from models.user_config import UserConfig
from core.config import settings
from core.security import (
    create_access_token, 
    verify_wallet_signature, 
    verify_password, 
    get_password_hash
)
from core.dependencies import get_current_user
from schemas.user import (
    ConnectRequest,
    TestConnectRequest,  # ✅ ДОБАВЛЯЕМ ИМПОРТ
    AuthResponse, 
    LoginRequest, 
    RegisterRequest,
    ShowUser
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== OAuth2 СТАНДАРТНЫЙ ЭНДПОИНТ ====================

@router.post("/token", response_model=AuthResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Стандартный OAuth2 эндпоинт для получения токена.
    Используется Swagger UI для авторизации.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status == UserStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked"
        )

    if user.status == UserStatus.PENDING and user.wallet_type == "EMAIL":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )

    user.last_login_at = func.now()
    user.last_active = func.now()
    db.commit()

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ==================== WEB3 АУТЕНТИФИКАЦИЯ ====================

@router.post("/connect", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def connect_wallet(
    request: ConnectRequest, 
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя через криптографический подпись кошелька Web3
    """
    wallet_address = request.wallet_address
    message = request.message
    signature = request.signature

    if not verify_wallet_signature(wallet_address, message, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid wallet signature"
        )

    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    
    if not user:
        user = User(
            wallet_address=wallet_address, 
            wallet_type="EVM", 
            status=UserStatus.ACTIVE,
            role="user"
        )
        profile = Profile(user=user)
        config = UserConfig(user=user)
        db.add_all([user, profile, config])
        db.commit()
        db.refresh(user)

    user.last_active = func.now()
    db.commit()

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ==================== ТЕСТОВЫЙ ЭНДПОИНТ ДЛЯ SWAGGER (WEB3) ====================

@router.post("/connect/test", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def test_connect_wallet(
    request: TestConnectRequest,
    db: Session = Depends(get_db)
):
    """
    ⚠️ ТЕСТОВЫЙ эндпоинт для быстрой авторизации через кошелёк (только для разработки!)
    Не используйте в продакшене!
    """
    wallet_address = request.wallet_address
    
    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    
    if not user:
        is_admin = wallet_address == os.getenv("ADMIN_WALLET_ADDRESS", "0x90F8bf6A479f320ced073E5743F257356671B414")
        
        user = User(
            wallet_address=wallet_address,
            wallet_type="EVM",
            status=UserStatus.ACTIVE,
            role="admin" if is_admin else "user",
            display_name="Crypto Admin" if is_admin else "Test User",
            has_paid_entrance=True
        )
        profile = Profile(user=user)
        config = UserConfig(user=user)
        db.add_all([user, profile, config])
        db.commit()
        db.refresh(user)
    
    user.last_active = func.now()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ==================== EMAIL АУТЕНТИФИКАЦИЯ ====================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Регистрация пользователя по email и паролю
    """
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if request.wallet_address:
        existing_wallet = db.query(User).filter(User.wallet_address == request.wallet_address).first()
        if existing_wallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wallet address already registered"
            )

    hashed_password = get_password_hash(request.password)

    user = User(
        wallet_address=request.wallet_address or f"email_{request.email}",
        wallet_type=None,
        email=request.email,
        hashed_password=hashed_password,
        is_email_verified=False,
        display_name=request.display_name,
        status=UserStatus.PENDING,
        role="user"
    )

    profile = Profile(user=user)
    config = UserConfig(user=user)
    db.add_all([user, profile, config])
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Вход по email и паролю
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if user.status == UserStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked"
        )

    if user.status == UserStatus.PENDING and user.wallet_type == "EMAIL":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )

    user.last_login_at = func.now()
    user.last_active = func.now()
    db.commit()

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    """
    Выход из системы (клиент удаляет токен)
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=ShowUser)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе
    """
    return current_user