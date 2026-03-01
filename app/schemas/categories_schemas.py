from pydantic import BaseModel, Field, ConfigDict, field_validator



class CategoryCreateSchema(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name : str = Field(min_length=0, max_length=50, description='НАзвание категории')
    parent_id : int | None = Field(default=None, description='Id родительской категории если есть')
    
    


class CategorySchena(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах и ответах юзеру на запрос.
    """
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")
    is_active: bool = Field(..., description="Активность категории")

    model_config = ConfigDict(from_attributes=True) # для преобразования объектов sqlalchemy в pydantic модели для ответа юзеру
