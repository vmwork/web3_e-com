"""Initial migration

Revision ID: 02592f27c634
Revises: 
Create Date: 2026-07-30 14:28:06.256116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '02592f27c634'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # ВСЕ CREATE TABLE И CREATE INDEX (БЕЗ DROP)
    # ============================================================
    
    # 1. Таблица users
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('wallet_address', sa.String(length=100), nullable=True),
        sa.Column('wallet_type', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=True),
        sa.Column('has_paid_entrance', sa.Boolean(), nullable=True),
        sa.Column('paid_entrance_at', sa.DateTime(), nullable=True),
        sa.Column('total_slots', sa.Integer(), nullable=True),
        sa.Column('used_slots', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('total_deals', sa.Integer(), nullable=True),
        sa.Column('positive_deals', sa.Integer(), nullable=True),
        sa.Column('subscription_type', sa.String(length=20), nullable=True),
        sa.Column('subscription_until', sa.DateTime(), nullable=True),
        sa.Column('fee_percent', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'BLOCKED', 'PENDING', 'DANGER', name='userstatus'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('display_name', sa.String(length=50), nullable=True),
        sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('wallet_address')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_wallet_address', 'users', ['wallet_address'], unique=True)
    op.create_index('ix_users_status_role', 'users', ['status', 'role'], unique=False)
    op.create_index('ix_users_subscription_until', 'users', ['subscription_until'], unique=False)

    # 2. Таблица profiles
    op.create_table('profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('social_links', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_profiles_id', 'profiles', ['id'], unique=False)

    # 3. Таблица user_configs
    op.create_table('user_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('notifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('privacy', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('additional_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_configs_id', 'user_configs', ['id'], unique=False)

    # 4. Таблица categories
    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('icon', sa.String(length=255), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_categories_id', 'categories', ['id'], unique=False)
    op.create_index('ix_categories_parent_id', 'categories', ['parent_id'], unique=False)
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=True)

    # 5. Таблица products
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seller_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.String(length=500), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_mime_type', sa.String(length=100), nullable=True),
        sa.Column('download_limit', sa.Integer(), nullable=True),
        sa.Column('is_downloadable', sa.Boolean(), nullable=True),
        sa.Column('status', postgresql.ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED', name='productstatus'), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('preview_images', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preview_video', sa.String(length=500), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('purchases_count', sa.Integer(), nullable=True),
        sa.Column('rating_avg', sa.Float(), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=True),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.String(length=500), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'], unique=False)
    op.create_index('ix_products_category_status', 'products', ['category_id', 'status'], unique=False)
    op.create_index('ix_products_created_at', 'products', ['created_at'], unique=False)
    op.create_index('ix_products_status_price', 'products', ['status', 'price'], unique=False)

    # 6. Таблица orders
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=True),
        sa.Column('discount_amount', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'PAID', 'COMPLETED', 'FAILED', 'REFUNDED', 'CANCELLED', name='orderstatus'), nullable=True),
        sa.Column('buyer_email', sa.String(length=255), nullable=True),
        sa.Column('buyer_wallet', sa.String(length=100), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_tx_hash', sa.String(length=255), nullable=True),
        sa.Column('payment_currency', sa.String(length=10), nullable=True),
        sa.Column('payment_amount', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index('ix_orders_id', 'orders', ['id'], unique=False)
    op.create_index('ix_orders_buyer_status', 'orders', ['buyer_id', 'status'], unique=False)
    op.create_index('ix_orders_created_at', 'orders', ['created_at'], unique=False)
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_status', 'orders', ['status'], unique=False)

    # 7. Таблица order_items
    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_title', sa.String(length=255), nullable=False),
        sa.Column('product_price', sa.Float(), nullable=False),
        sa.Column('product_file_path', sa.String(length=500), nullable=False),
        sa.Column('product_file_name', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('download_count', sa.Integer(), nullable=True),
        sa.Column('last_download_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_items_id', 'order_items', ['id'], unique=False)

    # 8. Таблица reviews
    op.create_table('reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_verified_purchase', sa.Boolean(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'], unique=False)
    op.create_index('ix_reviews_product_rating', 'reviews', ['product_id', 'rating'], unique=False)
    op.create_index('ix_reviews_user_product', 'reviews', ['user_id', 'product_id'], unique=True)

    # 9. Таблица download_tokens
    op.create_table('download_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_download_tokens_id', 'download_tokens', ['id'], unique=False)
    op.create_index('ix_download_tokens_token', 'download_tokens', ['token'], unique=True)
    op.create_index('ix_download_tokens_token_expires', 'download_tokens', ['token', 'expires_at'], unique=False)


def downgrade() -> None:
    # ============================================================
    # ОТКАТ (удаление таблиц в обратном порядке)
    # ============================================================
    op.drop_table('download_tokens')
    op.drop_table('reviews')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('user_configs')
    op.drop_table('profiles')
    op.drop_table('users')
    
    # Удаляем ENUM типы (если они были созданы)
    op.execute('DROP TYPE IF EXISTS userstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS productstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS orderstatus CASCADE')