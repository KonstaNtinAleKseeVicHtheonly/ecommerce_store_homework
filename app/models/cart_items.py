from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base


class CartItemModel(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
    ) # Это ограничение уникальности гарантирует, что один и тот же товар не может быть добавлен в корзину пользователя дважды.(при повторном добавлении увеличит количество товара на 1)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1) # сколько единц определенного товара хранится в корзине
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    
    user : Mapped['UserModel'] = relationship('UserModel', back_populates='cart_items')
    product : Mapped['ProductModel'] = relationship('ProductModel', back_populates='cart_items')
