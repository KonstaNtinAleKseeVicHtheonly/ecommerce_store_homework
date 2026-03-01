from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from decimal import Decimal


class UserCreateSchema(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    email: EmailStr = Field(description="Email юзера")
    password: str = Field(min_length=8, description="Пароль (от 8 символов)")
    role: str = Field(default='buyer', pattern="^(buyer|seller)$",  description="Роль: 'buyer' или 'seller'")
    
    
    
class UserSchema(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """

    id: int = Field(..., description="Уникальный идентификатор ,pthf")
    email: str = Field(..., description="email юзера")
    role: str = Field(description="Роль юзера")
    is_active: bool = Field(..., description="Активность категории")
    
    model_config = ConfigDict(from_attributes=True) # для интеграции с ORM