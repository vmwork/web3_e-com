from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from db.session import get_db
from models.user import User
from schemas.user import ShowUser, UserUpdate, PasswordChangeRequest
from core.dependencies import get_current_user
from core.security import verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ShowUser)
def get_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем авторизованном пользователе"""
    return current_user


@router.put("/me", response_model=ShowUser)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные аккаунта"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "email" and value:
            # Проверяем, не занят ли email
            existing = db.query(User).filter(
                User.email == value,
                User.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", status_code=status.HTTP_200_OK)
def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сменить пароль"""
    # Если у пользователя нет пароля (Web3-кошелёк)
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Web3 authentication, no password set"
        )
    
    # Проверяем старый пароль
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password"
        )
    
    # Хешируем новый пароль
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/me/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Подтверждение email (заглушка, TODO: добавить отправку письма с кодом)
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    current_user.is_email_verified = True
    if current_user.status == UserStatus.PENDING:
        current_user.status = UserStatus.ACTIVE
    
    db.commit()
    return {"message": "Email verified successfully"}