from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User
from models.profile import Profile
from schemas.profile import ShowProfile, ProfileUpdate
from core.dependencies import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/me", response_model=ShowProfile)
def get_my_profile(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Получить профиль текущего пользователя"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()  # ✅ user.id
    
    # Если профиля нет — создаём (на всякий случай)
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile

@router.put("/me", response_model=ShowProfile)
def update_my_profile(
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные профиля"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()  # ✅ user.id
    
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile