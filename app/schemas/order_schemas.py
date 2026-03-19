from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from app.schemas.products_schemas import ProductSchema
from datetime import datetime

class OrderItemSchema(BaseModel):
    """
    схема для валидации опред товара в опред заказе; стоимость количестов
    Свяазан с схемой продуктов
    """
    id: int = Field(..., description="ID позиции заказа")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., ge=1, description="Количество")
    unit_price: Decimal = Field(..., ge=0, description="Цена за единицу на момент покупки")
    total_price: Decimal = Field(..., ge=0, description="Сумма по позиции")
    product: ProductSchema | None = Field(None, description="Полная информация о товаре")

    model_config = ConfigDict(from_attributes=True)
    
    
class OrderSchema(BaseModel):
    """
    схема для валидации и вывода инфы об опред заказе - статус, количество позиций.
    """
    id: int = Field(..., description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость")
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItemSchema] = Field(default_factory=list, description="Список позиций") # связь с опред товаром

    model_config = ConfigDict(from_attributes=True)
    
class OrderListSchema(BaseModel):
    '''схема валидации всех заказов юзера'''
    items : list[OrderSchema] = Field(..., description='Список всех заказов юзера')
    total: int = Field(...,ge=0, description="Общее количество заказов")
    page:  int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество заказов на странице")
    model_config = ConfigDict(from_attributes=True)
    
class OrderCheckoutResponseSchema(BaseModel):
    '''схема для валидации данных о заказе когда отправляем данные о заказе юзеру 
    при создании платежа. Именно она будет отправлять клиенту данные полученные от YooKassa 
    при создании платежа'''
    order: OrderSchema = Field(..., description="Созданный заказ")
    confirmation_url: str | None = Field(
        None,
        description="URL для перехода на оплату в YooKassa")
    