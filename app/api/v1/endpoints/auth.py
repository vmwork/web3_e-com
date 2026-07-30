from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

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
from schemas.user import (
    ConnectRequest, 
    AuthResponse, 
    LoginRequest, 
    RegisterRequest,
    ShowUser
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
        # Создаём связанные профили
        profile = Profile(user=user)
        config = UserConfig(user=user)
        db.add_all([user, profile, config])
        db.commit()
        db.refresh(user)

    # Обновляем last_active
    user.last_active = func.now()
    db.commit()

    # Создаём токен с user.id
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
    # Проверка на существование email
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Проверка на существование wallet_address (если указан)
    if request.wallet_address:
        existing_wallet = db.query(User).filter(User.wallet_address == request.wallet_address).first()
        if existing_wallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wallet address already registered"
            )

    # Хешируем пароль
    hashed_password = get_password_hash(request.password)

    # Создаём пользователя
    user = User(
        wallet_address=request.wallet_address or f"email_{request.email}",  # заглушка
        wallet_type="EMAIL",
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

    # Создаём токен
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
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Проверяем пароль
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Проверяем статус
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

    # Обновляем last_login_at и last_active
    user.last_login_at = func.now()
    user.last_active = func.now()
    db.commit()

    # Создаём токен
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