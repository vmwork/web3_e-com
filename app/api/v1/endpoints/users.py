from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User
from schemas.user import ShowUser, UserUpdate
from core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=ShowUser)
def get_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем авторизованном кошельке"""
    return current_user

@router.put("/me", response_model=ShowUser)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить метаданные аккаунта кошелька (display_name)"""
    if user_update.display_name is not None:
        current_user.display_name = user_update.display_name
    db.commit()
    db.refresh(current_user)
    return current_user
