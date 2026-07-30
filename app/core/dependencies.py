from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from models.user import User, UserStatus
from core.security import verify_token

# ✅ Используем OAuth2PasswordBearer, а не HTTPBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),  # ✅ token как str
    db: Session = Depends(get_db)
) -> User:
    """
    Зависимость для получения текущего пользователя.
    Поддерживает как Web3 (wallet_address), так и email-аутентификацию (user_id).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception

    # Пробуем получить user_id (для email-аутентификации)
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Пробуем найти пользователя по ID (UUID)
    try:
        user_uuid = UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
    except (ValueError, TypeError):
        # Если не UUID, пробуем найти по wallet_address (для обратной совместимости)
        user = db.query(User).filter(User.wallet_address == user_id).first()

    if user is None:
        raise credentials_exception

    if user.status == UserStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked by administration"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяет, что пользователь активен"""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяет, что пользователь админ"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user