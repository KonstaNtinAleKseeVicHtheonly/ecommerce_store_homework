from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Numeric, BigInteger, DateTime, Float, Computed
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import Index, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TSVECTOR



class ProductModel(Base):
    __tablename__ = "products"
    
    # индексы
    __table_args__ = (Index("ix_products_tsv_gin", 'tsv', postgresql_using='gin'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # внешние ключи
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index = True)  # New
    category_id : Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'), nullable=False, index = True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float] = mapped_column(
        Numeric(2, 1),          
        nullable=False,
        server_default=text('0.0'),
        default=0.0)
    #TSP поиск для gin индекса 
    tsv: Mapped[TSVECTOR] = mapped_column(
                TSVECTOR,
                Computed(
                    """
            setweight(to_tsvector('russian', coalesce(name, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
            setweight(to_tsvector('russian', coalesce(description, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(description, '')), 'B')
                    """,
                    persisted=True,
                ),# A, B приоритеты (по убыванию от A до D)
                nullable=False,
            )
    
    #отношения к таблицам
    category : Mapped["CategoryModel"] = relationship("CategoryModel", back_populates='products')
    seller : Mapped['UserModel'] = relationship("UserModel", back_populates='products')
    product_reviews : Mapped['ReviewModel'] = relationship('ReviewModel', back_populates='product')
    cart_items : Mapped[list['CartItemModel']] = relationship('CartItemModel', back_populates='product', cascade="all, delete-orphan")        
    order_items : Mapped[list['OrderItemModel']] = relationship('OrderItemModel', back_populates='product')
    