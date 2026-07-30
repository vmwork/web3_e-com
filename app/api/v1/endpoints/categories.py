from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from db.session import get_db
from models.category import Category
from models.user import User
from schemas.category import CategoryCreate, CategoryUpdate, ShowCategory
from core.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[ShowCategory])
def get_categories(
    parent_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """
    Получить список категорий
    - parent_id: фильтр по родительской категории (null = корневые)
    - is_active: фильтр по активности
    """
    query = db.query(Category)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id.is_(None))
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    categories = query.order_by(Category.sort_order, Category.name).all()
    return categories


@router.get("/{category_id}", response_model=ShowCategory)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить категорию по ID
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get("/slug/{slug}", response_model=ShowCategory)
def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Получить категорию по slug
    """
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


# ==================== АДМИН-ЭНДПОИНТЫ ====================

@router.post("/", response_model=ShowCategory, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Создать категорию (только для админа)
    """
    # Проверка на существование slug
    existing = db.query(Category).filter(Category.slug == category_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists"
        )
    
    # Проверка родительской категории
    if category_data.parent_id:
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found"
            )
    
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=ShowCategory)
def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Обновить категорию (только для админа)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Проверка slug на уникальность
    if category_data.slug and category_data.slug != category.slug:
        existing = db.query(Category).filter(Category.slug == category_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )
    
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Удалить категорию (только для админа)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Проверка на наличие дочерних категорий
    children = db.query(Category).filter(Category.parent_id == category_id).first()
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with children"
        )
    
    db.delete(category)
    db.commit()
    return None