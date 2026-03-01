from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Numeric, BigInteger, DateTime, Float
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import Index, UniqueConstraint, text



class ProductModel(Base):
    __tablename__ = "products"
    
    # индексы
    __table_args__ = (
    Index('idx_products_seller', 'seller_id'),
    Index('idx_products_category', 'category_id'))

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
    
    
    #отношения к таблицам
    category : Mapped["CategoryModel"] = relationship("CategoryModel", back_populates='products')
    seller : Mapped['UserModel'] = relationship("UserModel", back_populates='products')
    product_reviews : Mapped['ReviewModel'] = relationship('ReviewModel', back_populates='product')
    