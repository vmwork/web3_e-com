from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID

from db.session import get_db
from models.review import Review
from models.product import Product
from models.order import Order, OrderStatus
from models.user import User
from schemas.review import ReviewCreate, ReviewUpdate, ShowReview
from core.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/products/{product_id}", response_model=List[ShowReview])
def get_product_reviews(
    product_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Получить отзывы на продукт
    """
    reviews = db.query(Review).options(
        joinedload(Review.user)
    ).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    ).order_by(
        Review.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return reviews


@router.post("/", response_model=ShowReview, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать отзыв на продукт
    """
    # Проверка: продукт существует
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Проверка: пользователь не оставлял отзыв ранее
    existing = db.query(Review).filter(
        Review.product_id == review_data.product_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already reviewed this product"
        )
    
    # Проверка: пользователь купил этот товар (для verified purchase)
    is_verified = False
    if review_data.order_id:
        order = db.query(Order).filter(
            Order.id == review_data.order_id,
            Order.buyer_id == current_user.id,
            Order.status == OrderStatus.COMPLETED
        ).first()
        if order:
            is_verified = True
    
    review = Review(
        **review_data.model_dump(),
        user_id=current_user.id,
        is_verified_purchase=is_verified,
        is_approved=False  # Требуется модерация
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Обновляем рейтинг продукта
    update_product_rating(db, review_data.product_id)
    
    return review


@router.put("/{review_id}", response_model=ShowReview)
def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить свой отзыв
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Проверка: только автор может редактировать
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = review_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)
    
    db.commit()
    db.refresh(review)
    
    # Обновляем рейтинг продукта
    update_product_rating(db, review.product_id)
    
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить свой отзыв
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Проверка: только автор или админ могут удалить
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product_id = review.product_id
    db.delete(review)
    db.commit()
    
    # Обновляем рейтинг продукта
    update_product_rating(db, product_id)
    
    return None


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def update_product_rating(db: Session, product_id: UUID):
    """Обновить средний рейтинг продукта"""
    from sqlalchemy import func as sa_func
    
    result = db.query(
        sa_func.avg(Review.rating).label('avg_rating'),
        sa_func.count(Review.id).label('count')
    ).filter(
        Review.product_id == product_id,
        Review.is_approved == True
    ).first()
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.rating_avg = result.avg_rating or 0.0
        product.rating_count = result.count or 0
        db.commit()


# ==================== АДМИН-ЭНДПОИНТЫ ====================

@router.get("/admin/pending", response_model=List[ShowReview])
def get_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Получить отзывы, ожидающие модерации (для админа)
    """
    reviews = db.query(Review).filter(Review.is_approved == False).order_by(
        Review.created_at.desc()
    ).all()
    return reviews


@router.put("/admin/{review_id}/approve", response_model=ShowReview)
def approve_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Одобрить отзыв (для админа)
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.is_approved = True
    db.commit()
    db.refresh(review)
    
    # Обновляем рейтинг продукта
    update_product_rating(db, review.product_id)
    
    return review