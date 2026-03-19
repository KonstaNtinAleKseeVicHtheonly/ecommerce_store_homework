from decimal import Decimal

from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Integer, DateTime, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime


from app.core.database import Base


class OrderModel(Base):
    '''модель которая объединяет все заказы юзера,  СОдержит обую инфу а статусе, времени создания и обновления товаров, количестве заказов'''
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status : Mapped[str] = mapped_column(String(20), default="pending", nullable=False) # статус заказа
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    payment_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_amount : Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    
    user : Mapped['UserModel'] = relationship('UserModel', back_populates='user_orders')
    items : Mapped[list['OrderItemModel']] = relationship('OrderItemModel', back_populates='total_order', cascade="all, delete-orphan")# при удаление основного заказа все  его позиции также удаляются
    
    
class OrderItemModel(Base):
    '''модель для детального отображения текущего товара в заказе юзера, учитывая его цену сохранением стоимости на момент покупки и т.д, количество'''
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id : Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False) # ценка за одну ед. товара на момент формирования заказа(для статистики)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)# цена за все количество данного товара для дальнейшних вычислений

    
    
    total_order : Mapped['OrderModel'] = relationship('OrderModel', back_populates='items')
    product : Mapped['ProductModel'] = relationship('ProductModel', back_populates='order_items')

