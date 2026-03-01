from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from datetime import datetime


class ReviewCreateSchema(BaseModel):
    """
    Модель для создания и обновления отзыва.
    Используется в POST и PUT запросах.
    """
    
    product_id: int = Field(..., description="id продукта под отзыв")
    comment : str = Field(..., min_length=5, max_length=100,
                      description="Текст отзыва(от 5 до 100 символов)")
    grade : int =  Field(..., description="оценка за товар (от 1 до 5)")

    
    
class ReviewSchema(BaseModel):
    """
    Модель для ответа с данными отзыва.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор товара")
    product_id: int = Field(..., description="id продукта под отзыв")
    user_id : int = Field(..., description="id юзера оставившего отзыв")
    comment : str = Field(..., min_length=5, max_length=100,
                      description="Текст отзыва(от 5 до 100 символов)")
    grade : int =  Field(ge=1, le=5, description="оценка за товар (от 1 до 5)")
    is_active: bool = Field(..., description="Активность категории")
    comment_date : datetime = Field(..., description='дата создания товара')
    
    model_config = ConfigDict(from_attributes=True) # для интеграции с ORM